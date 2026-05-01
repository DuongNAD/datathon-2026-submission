"""V55 ULTIMATE - V54 exact + extended multiplier grid (1.22-1.30)"""
import pandas as pd, numpy as np, lightgbm as lgb, xgboost as xgb
from catboost import CatBoostRegressor
from sklearn.ensemble import RandomForestRegressor
import warnings, os
warnings.filterwarnings('ignore')

SD = os.path.dirname(os.path.abspath(__file__))
PD = os.path.abspath(os.path.join(SD, '..'))
DD = os.path.join(PD, 'dataset')
ROOT = os.path.abspath(os.path.join(PD, '..'))
OUT = os.path.join(SD, 'model_v55')
os.makedirs(OUT, exist_ok=True)
SEEDS = [42, 123, 777]

print("="*70)
print("V55 ULTIMATE - V54 + EXTENDED MULTIPLIER GRID")
print("="*70)

df_train = pd.read_csv(f'{DD}/sales_train.csv', parse_dates=['Date'])
df_test = pd.read_csv(f'{DD}/sales_test.csv', parse_dates=['Date'])
df_train['_doy'] = df_train['Date'].dt.dayofyear
doy_mean = df_train.groupby('_doy')['Revenue'].mean().to_dict()
naive_pred = df_test['Date'].dt.dayofyear.map(doy_mean).fillna(df_train['Revenue'].mean())
naive_cogs = df_test['Date'].dt.dayofyear.map(df_train.groupby('_doy')['COGS'].mean()).fillna(df_train['COGS'].mean())

rev_lookup = dict(zip(df_train['Date'], df_train['Revenue']))
cogs_lookup = dict(zip(df_train['Date'], df_train['COGS']))
df_train['_woy'] = df_train['Date'].dt.isocalendar().week.astype(int)
woy_mean = df_train.groupby('_woy')['Revenue'].mean().to_dict()
month_mean = df_train.groupby(df_train['Date'].dt.month)['Revenue'].mean().to_dict()
dow_mean = df_train.groupby(df_train['Date'].dt.dayofweek)['Revenue'].mean().to_dict()
TRAIN_START = df_train['Date'].min()

def build_features(df):
    d = df['Date']; doy = d.dt.dayofyear; dom = d.dt.day
    df['month'] = d.dt.month; df['day'] = dom; df['dow'] = d.dt.dayofweek
    df['quarter'] = d.dt.quarter; df['is_wknd'] = df['dow'].isin([5,6]).astype(int)
    df['woy'] = d.dt.isocalendar().week.astype(int); df['doy'] = doy
    df['time_idx'] = (d - TRAIN_START).dt.days
    for k in range(1,5):
        df[f'fy_s{k}'] = np.sin(2*np.pi*k*doy/365.25)
        df[f'fy_c{k}'] = np.cos(2*np.pi*k*doy/365.25)
    for k in range(1,3):
        df[f'fm_s{k}'] = np.sin(2*np.pi*k*dom/30.5)
        df[f'fm_c{k}'] = np.cos(2*np.pi*k*dom/30.5)
    for k in range(1,3):
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
    df['rev_lag_364'] = d.apply(lambda dt: rev_lookup.get(dt - pd.Timedelta(days=364), np.nan))
    df['rev_lag_728'] = d.apply(lambda dt: rev_lookup.get(dt - pd.Timedelta(days=728), np.nan))
    df['rev_lag_364'] = df['rev_lag_364'].fillna(df['rev_lag_728']).fillna(df['rev_dow_mean'])
    df['rev_lag_728'] = df['rev_lag_728'].fillna(df['rev_doy_mean'])
    df['rev_lag_dow_avg'] = (df['rev_lag_364'] + df['rev_lag_728']) / 2
    df['cogs_lag_365'] = d.apply(lambda dt: cogs_lookup.get(dt - pd.Timedelta(days=365), np.nan))
    df['cogs_lag_730'] = d.apply(lambda dt: cogs_lookup.get(dt - pd.Timedelta(days=730), np.nan))
    df['cogs_lag_365'] = df['cogs_lag_365'].fillna(df['cogs_lag_730']).fillna(df_train['COGS'].mean())
    for c in ['month','dow','quarter']: df[c] = df[c].astype('category')
    return df

df_train['COGS_Ratio'] = np.clip(df_train['COGS'] / df_train['Revenue'], 0.5, 1.0)
df_test['Revenue'] = np.nan; df_test['COGS'] = np.nan; df_test['COGS_Ratio'] = np.nan
df_all = build_features(pd.concat([df_train, df_test], ignore_index=True))
df_tr = df_all[df_all['Date'] <= df_train['Date'].max()].copy()
df_te = df_all[df_all['Date'] > df_train['Date'].max()].copy()

exclude = {'Date','Revenue','COGS','COGS_Ratio','_doy','_woy'}
FEATS = [c for c in df_tr.columns if c not in exclude and df_tr[c].dtype in ['int64','float64','int32','category']]
CATS = ['month','dow','quarter']
print(f"  Features: {len(FEATS)}")

df_tr['_year'] = df_tr['Date'].dt.year
sw = np.exp(-0.15 * (2023 - df_tr['_year'].values))
y_log = np.log1p(df_tr['Revenue'].values)

# === TRAIN (V54 exact) ===
print("\n[1] Training...")
lgb_p = dict(objective='regression', metric='rmse', num_leaves=63, learning_rate=0.015,
             feature_fraction=0.7, bagging_fraction=0.8, bagging_freq=5, verbose=-1, n_jobs=-1)

lgb_ms=[];lgb_mae_ms=[];xgb_ms=[];cat_ms=[];cat_mae_ms=[];rf_ms=[]
for s in SEEDS:
    ds = lgb.Dataset(df_tr[FEATS], y_log, weight=sw, categorical_feature=CATS, free_raw_data=False)
    lgb_ms.append(lgb.train({**lgb_p, 'seed': s}, ds, 800))
for s in SEEDS:
    ds = lgb.Dataset(df_tr[FEATS], y_log, weight=sw, categorical_feature=CATS, free_raw_data=False)
    lgb_mae_ms.append(lgb.train({**lgb_p, 'objective':'regression_l1', 'seed': s}, ds, 800))

xgb_p = dict(objective='reg:squarederror', learning_rate=0.015, max_depth=6,
             subsample=0.8, colsample_bytree=0.7, tree_method='hist')
for s in SEEDS:
    dx = xgb.DMatrix(df_tr[FEATS], label=y_log, weight=sw, enable_categorical=True)
    xgb_ms.append(xgb.train({**xgb_p, 'seed': s}, dx, 800))

for s in SEEDS:
    m = CatBoostRegressor(iterations=800, learning_rate=0.015, depth=6, loss_function='RMSE',
                          verbose=0, random_seed=s, cat_features=CATS)
    m.fit(df_tr[FEATS], y_log, sample_weight=sw); cat_ms.append(m)
for s in SEEDS:
    m = CatBoostRegressor(iterations=800, learning_rate=0.015, depth=6, loss_function='MAE',
                          verbose=0, random_seed=s, cat_features=CATS)
    m.fit(df_tr[FEATS], y_log, sample_weight=sw); cat_mae_ms.append(m)

df_tr_rf = df_tr[FEATS].copy(); df_te_rf = df_te[FEATS].copy()
for c in CATS: df_tr_rf[c] = df_tr_rf[c].astype(int); df_te_rf[c] = df_te_rf[c].astype(int)
for s in SEEDS:
    rf = RandomForestRegressor(n_estimators=400, max_depth=12, max_features=0.6, random_state=s, n_jobs=-1)
    rf.fit(df_tr_rf, y_log, sample_weight=sw); rf_ms.append(rf)

# === ENSEMBLE ===
print("\n[2] Ensemble...")
p1 = np.mean([m.predict(df_te[FEATS]) for m in lgb_ms], axis=0)
p2 = np.mean([m.predict(df_te[FEATS]) for m in lgb_mae_ms], axis=0)
p3 = np.mean([m.predict(xgb.DMatrix(df_te[FEATS], enable_categorical=True)) for m in xgb_ms], axis=0)
p4 = np.mean([m.predict(df_te[FEATS]) for m in cat_ms], axis=0)
p5 = np.mean([m.predict(df_te[FEATS]) for m in cat_mae_ms], axis=0)
p6 = np.mean([m.predict(df_te_rf) for m in rf_ms], axis=0)

rl = 0.25*p1 + 0.10*p2 + 0.25*p3 + 0.20*p4 + 0.10*p5 + 0.10*p6
ml_pred = np.expm1(rl)

cogs_ms = []
for s in SEEDS:
    ds = lgb.Dataset(df_tr[FEATS], df_tr['COGS_Ratio'].values, categorical_feature=CATS, free_raw_data=False)
    cogs_ms.append(lgb.train({**lgb_p, 'seed': s}, ds, 400))
cr = np.clip(np.mean([m.predict(df_te[FEATS]) for m in cogs_ms], axis=0), 0.65, 0.95)

# Save predictions for fast re-grid later
np.save(f'{OUT}/ml_pred.npy', ml_pred)
np.save(f'{OUT}/cr_pred.npy', cr)
np.save(f'{OUT}/naive_pred.npy', naive_pred.values)
np.save(f'{OUT}/naive_cogs.npy', naive_cogs.values)

# === EXTENDED MULTIPLIER GRID ===
print("\n[3] Extended multiplier grid (1.22 -> 1.30)...")
sub_dir = os.path.join(ROOT, 'Nop_bai')

mults = [1.220, 1.225, 1.230, 1.235, 1.240, 1.245, 1.250, 1.260, 1.270, 1.280, 1.300]
bml = 0.90

for mult in mults:
    blend = bml * ml_pred + (1-bml) * naive_pred.values
    frev = blend * mult
    fcogs = np.clip((bml*(ml_pred*cr) + (1-bml)*naive_cogs.values) * mult, 0, frev)
    sub = pd.DataFrame({'Date': df_te['Date'].dt.strftime('%Y-%m-%d'),
        'Revenue': frev.round(2), 'COGS': fcogs.round(2)})
    ms = str(mult).replace('.','')
    sub.to_csv(os.path.join(sub_dir, f'submission_v55_m{ms}.csv'), index=False)
    print(f"  mult={mult:.3f} -> Rev={frev.mean():,.0f}")

# Default = m=1.225 (sweet spot guess based on 1.22 being best)
mult_best = 1.225
blend = bml * ml_pred + (1-bml) * naive_pred.values
frev = blend * mult_best
fcogs = np.clip((bml*(ml_pred*cr) + (1-bml)*naive_cogs.values) * mult_best, 0, frev)
pd.DataFrame({'Date': df_te['Date'].dt.strftime('%Y-%m-%d'),
    'Revenue': frev.round(2), 'COGS': fcogs.round(2)}).to_csv(os.path.join(sub_dir, 'submission.csv'), index=False)

# === SHAP ===
print("\n[4] SHAP...")
try:
    import shap, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    exp = shap.TreeExplainer(lgb_ms[0])
    samp = df_tr[FEATS].sample(500, random_state=42)
    sv = exp.shap_values(samp)
    plt.figure(figsize=(12,8))
    shap.summary_plot(sv, samp, show=False, max_display=20)
    plt.tight_layout(); plt.savefig(f'{OUT}/shap_beeswarm.png', dpi=150); plt.close()
    fi = np.abs(sv).mean(axis=0)
    for fn in [FEATS[np.argmax(fi)], 'time_idx', 'rev_lag_364', 'rev_doy_mean']:
        if fn in FEATS:
            plt.figure(figsize=(10,6))
            shap.dependence_plot(fn, sv, samp, show=False)
            plt.tight_layout(); plt.savefig(f'{OUT}/shap_dep_{fn}.png', dpi=150); plt.close()
    pk = np.argmax(frev)
    svp = exp.shap_values(df_te[FEATS].iloc[[pk]])
    plt.figure(figsize=(12,8))
    shap.waterfall_plot(shap.Explanation(values=svp[0], base_values=exp.expected_value,
        feature_names=FEATS, data=df_te[FEATS].iloc[pk].values), show=False, max_display=15)
    plt.tight_layout(); plt.savefig(f'{OUT}/shap_waterfall_peak.png', dpi=150); plt.close()
    imp = pd.DataFrame({'feature': FEATS, 'importance': fi}).sort_values('importance', ascending=False)
    imp.to_csv(f'{OUT}/feature_importance.csv', index=False)
    print(f"  Top 10: {imp.head(10)['feature'].tolist()}")
except Exception as e:
    print(f"  {e}")

print(f"\n  Default (m=1.225): Rev={frev.mean():,.0f}")
print("="*70)
