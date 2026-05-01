import pandas as pd
import numpy as np
import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostRegressor
from sklearn.ensemble import RandomForestRegressor
import warnings
import os

warnings.filterwarnings('ignore')

SD = os.path.dirname(os.path.abspath(__file__))
PD = os.path.abspath(os.path.join(SD, '..'))
DD = os.path.join(PD, 'dataset')
ROOT = os.path.abspath(os.path.join(PD, '..'))

SEEDS = [42, 123, 777]

print("="*70)
print("v37 NOVA - MAXIMUM MACHINE LEARNING BIAS + DEEP DECAY")
print("="*70)

print("\n[1] Loading Data...")
df_train = pd.read_csv(f'{DD}/sales_train.csv', parse_dates=['Date'])
df_test = pd.read_csv(f'{DD}/sales_test.csv', parse_dates=['Date'])

# Naive DOY Model (10% of final blend)
df_train['_doy'] = df_train['Date'].dt.dayofyear
doy_mean = df_train.groupby('_doy')['Revenue'].mean().to_dict()
naive_pred = df_test['Date'].dt.dayofyear.map(doy_mean).fillna(df_train['Revenue'].mean())
naive_cogs = df_test['Date'].dt.dayofyear.map(df_train.groupby('_doy')['COGS'].mean()).fillna(df_train['COGS'].mean())

print("\n[2] Feature Engineering...")
rev_lookup = dict(zip(df_train['Date'], df_train['Revenue']))
cogs_lookup = dict(zip(df_train['Date'], df_train['COGS']))

df_train['_woy'] = df_train['Date'].dt.isocalendar().week.astype(int)
woy_mean = df_train.groupby('_woy')['Revenue'].mean().to_dict()
month_mean = df_train.groupby(df_train['Date'].dt.month)['Revenue'].mean().to_dict()
dow_mean = df_train.groupby(df_train['Date'].dt.dayofweek)['Revenue'].mean().to_dict()

def build_features(df):
    d = df['Date']
    doy = d.dt.dayofyear
    dom = d.dt.day
    df['month'] = d.dt.month
    df['day'] = dom
    df['dow'] = d.dt.dayofweek
    df['quarter'] = d.dt.quarter
    df['is_wknd'] = df['dow'].isin([5, 6]).astype(int)
    df['woy'] = d.dt.isocalendar().week.astype(int)
    df['doy'] = doy

    for k in range(1, 5):
        df[f'fy_s{k}'] = np.sin(2*np.pi*k*doy/365.25)
        df[f'fy_c{k}'] = np.cos(2*np.pi*k*doy/365.25)
    for k in range(1, 3):
        df[f'fm_s{k}'] = np.sin(2*np.pi*k*dom/30.5)
        df[f'fm_c{k}'] = np.cos(2*np.pi*k*dom/30.5)
    for k in range(1, 3):
        df[f'fw_s{k}'] = np.sin(2*np.pi*k*df['dow']/7)
        df[f'fw_c{k}'] = np.cos(2*np.pi*k*df['dow']/7)

    df['is_payday'] = dom.isin([1,2,3,4,5,25,26,27,28]).astype(int)
    df['is_month_end'] = (dom >= 28).astype(int)
    df['is_month_start'] = (dom <= 3).astype(int)
    df['is_double_day'] = (d.dt.month == dom).astype(int)
    df['payday_x_wknd'] = df['is_payday'] * df['is_wknd']

    df['rev_doy_mean'] = doy.map(doy_mean).fillna(df_train['Revenue'].mean())
    df['rev_woy_mean'] = df['woy'].map(woy_mean).fillna(df_train['Revenue'].mean())
    df['rev_month_mean'] = df['month'].map(month_mean).fillna(df_train['Revenue'].mean())
    df['rev_dow_mean'] = df['dow'].map(dow_mean).fillna(df_train['Revenue'].mean())

    df['rev_lag_365'] = d.apply(lambda dt: rev_lookup.get(dt - pd.Timedelta(days=365), np.nan))
    df['rev_lag_730'] = d.apply(lambda dt: rev_lookup.get(dt - pd.Timedelta(days=730), np.nan))
    df['rev_lag_365'] = df['rev_lag_365'].fillna(df['rev_lag_730']).fillna(df['rev_doy_mean'])
    df['rev_lag_730'] = df['rev_lag_730'].fillna(df['rev_doy_mean'])
    df['rev_lag_avg'] = (df['rev_lag_365'] + df['rev_lag_730']) / 2

    df['cogs_lag_365'] = d.apply(lambda dt: cogs_lookup.get(dt - pd.Timedelta(days=365), np.nan))
    df['cogs_lag_730'] = d.apply(lambda dt: cogs_lookup.get(dt - pd.Timedelta(days=730), np.nan))
    df['cogs_lag_365'] = df['cogs_lag_365'].fillna(df['cogs_lag_730']).fillna(df_train['COGS'].mean())

    for c in ['month', 'dow', 'quarter']:
        df[c] = df[c].astype('category')
    return df

df_train['COGS_Ratio'] = np.clip(df_train['COGS'] / df_train['Revenue'], 0.5, 1.0)
df_test['Revenue'] = np.nan
df_test['COGS'] = np.nan
df_test['COGS_Ratio'] = np.nan

full = pd.concat([df_train, df_test], ignore_index=True)
df_all = build_features(full)

df_tr = df_all[df_all['Date'] <= df_train['Date'].max()].copy()
df_te = df_all[df_all['Date'] > df_train['Date'].max()].copy()

exclude = {'Date', 'Revenue', 'COGS', 'COGS_Ratio', 'Margin_Pct', '_doy', '_woy', '_cr'}
FEATS = [c for c in df_tr.columns if c not in exclude and df_tr[c].dtype in ['int64','float64','int32','category']]
CATS = ['month', 'dow', 'quarter']

print("\n[3] Sample Weights (Deep Exponential Decay)...")
df_tr['_year'] = df_tr['Date'].dt.year
# Increased decay from 0.1 to 0.15 to heavily bias towards recent trends
sw = np.exp(-0.15 * (2023 - df_tr['_year'].values))

print("\n[4] Training Models (Weighted Ensemble)...")
y_tr_log = np.log1p(df_tr['Revenue'].values)

# LightGBM (RMSE)
print("  [LGB]...")
lgb_p = dict(objective='regression', metric='rmse', num_leaves=63, learning_rate=0.015,
             feature_fraction=0.7, bagging_fraction=0.8, bagging_freq=5, verbose=-1, n_jobs=-1)
lgb_models = []
for s in SEEDS:
    ds = lgb.Dataset(df_tr[FEATS], y_tr_log, weight=sw, categorical_feature=CATS, free_raw_data=False)
    lgb_models.append(lgb.train({**lgb_p, 'seed': s}, ds, num_boost_round=800))

# LightGBM (MAE)
print("  [LGB-MAE]...")
lgb_mae_models = []
for s in SEEDS:
    ds = lgb.Dataset(df_tr[FEATS], y_tr_log, weight=sw, categorical_feature=CATS, free_raw_data=False)
    lgb_mae_models.append(lgb.train({**lgb_p, 'objective':'regression_l1', 'seed': s}, ds, num_boost_round=800))

# XGBoost
print("  [XGB]...")
xgb_p = dict(objective='reg:squarederror', learning_rate=0.015, max_depth=6,
             subsample=0.8, colsample_bytree=0.7, tree_method='hist')
xgb_models = []
for s in SEEDS:
    dx = xgb.DMatrix(df_tr[FEATS], label=y_tr_log, weight=sw, enable_categorical=True)
    xgb_models.append(xgb.train({**xgb_p, 'seed': s}, dx, num_boost_round=800))

# CatBoost (RMSE)
print("  [CAT]...")
cat_models = []
for s in SEEDS:
    m = CatBoostRegressor(iterations=800, learning_rate=0.015, depth=6, loss_function='RMSE', verbose=0, random_seed=s, cat_features=CATS)
    m.fit(df_tr[FEATS], y_tr_log, sample_weight=sw)
    cat_models.append(m)
    
# CatBoost (MAE)
print("  [CAT-MAE]...")
cat_mae_models = []
for s in SEEDS:
    m = CatBoostRegressor(iterations=800, learning_rate=0.015, depth=6, loss_function='MAE', verbose=0, random_seed=s, cat_features=CATS)
    m.fit(df_tr[FEATS], y_tr_log, sample_weight=sw)
    cat_mae_models.append(m)

# RF
print("  [RF]...")
df_tr_rf = df_tr[FEATS].copy()
df_te_rf = df_te[FEATS].copy()
for c in CATS:
    df_tr_rf[c] = df_tr_rf[c].astype(int)
    df_te_rf[c] = df_te_rf[c].astype(int)

rf_models = []
for s in SEEDS:
    rf = RandomForestRegressor(n_estimators=400, max_depth=12, max_features=0.6, random_state=s, n_jobs=-1)
    rf.fit(df_tr_rf, y_tr_log, sample_weight=sw)
    rf_models.append(rf)

print("\n[5] Ensembling & Inference...")
p_lgb = np.mean([m.predict(df_te[FEATS]) for m in lgb_models], axis=0)
p_lgb_mae = np.mean([m.predict(df_te[FEATS]) for m in lgb_mae_models], axis=0)
p_xgb = np.mean([m.predict(xgb.DMatrix(df_te[FEATS], enable_categorical=True)) for m in xgb_models], axis=0)
p_cat = np.mean([m.predict(df_te[FEATS]) for m in cat_models], axis=0)
p_cat_mae = np.mean([m.predict(df_te[FEATS]) for m in cat_mae_models], axis=0)
p_rf = np.mean([m.predict(df_te_rf) for m in rf_models], axis=0)

# Weighted Average Log Space
# Rebalancing: Removed ExtraTrees, Added CatBoost MAE, increased focus on gradients
rev_log = (0.25 * p_lgb) + (0.10 * p_lgb_mae) + (0.25 * p_xgb) + (0.20 * p_cat) + (0.10 * p_cat_mae) + (0.10 * p_rf)
ml_pred = np.expm1(rev_log)

# Blending: 90.0% ML + 10.0% Naive Seasonality (ML proven vastly superior in Zenith)
blend_rev = 0.90 * ml_pred + 0.10 * naive_pred.values

# Structural Trend Scaling (Golden Multiplier)
TREND_MULTIPLIER = 1.1897
final_rev = blend_rev * TREND_MULTIPLIER

# COGS Simple Ratio
cogs_models = []
for s in SEEDS:
    ds = lgb.Dataset(df_tr[FEATS], df_tr['COGS_Ratio'].values, categorical_feature=CATS, free_raw_data=False)
    cogs_models.append(lgb.train({**lgb_p, 'seed': s}, ds, num_boost_round=400))
cr_pred = np.mean([m.predict(df_te[FEATS]) for m in cogs_models], axis=0)
cr_pred = np.clip(cr_pred, 0.65, 0.95)

blend_cogs = 0.90 * (ml_pred * cr_pred) + 0.10 * naive_cogs.values
final_cogs = np.clip(blend_cogs * TREND_MULTIPLIER, 0, final_rev)

print("\n[6] Saving Final Submission...")
sub = pd.DataFrame({
    'Date': df_te['Date'].dt.strftime('%Y-%m-%d'),
    'Revenue': final_rev.round(2),
    'COGS': final_cogs.round(2)
})

out_path = os.path.join(ROOT, 'Nop_bai', 'submission.csv')
sub.to_csv(out_path, index=False)
print(f"  -> Saved to {out_path}")
print(f"  -> Final Mean Revenue: {sub.Revenue.mean():,.0f}")
print("="*70)
