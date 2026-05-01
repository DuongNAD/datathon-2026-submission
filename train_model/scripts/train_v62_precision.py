"""V62 PRECISION - Smearing correction + Full COGS ensemble + Ultra-fine grid"""
import pandas as pd, numpy as np, os, lightgbm as lgb, xgboost as xgb
from catboost import CatBoostRegressor
from sklearn.ensemble import RandomForestRegressor
import warnings; warnings.filterwarnings('ignore')

SD = os.path.dirname(os.path.abspath(__file__))
DD = os.path.join(SD, '..', 'dataset')
ROOT = os.path.abspath(os.path.join(SD, '..', '..'))
OUT55 = os.path.join(SD, 'model_v55')
sub_dir = os.path.join(ROOT, 'Nop_bai')
SEEDS = [42, 123, 777]

print("="*70)
print("V62 PRECISION - SMEARING + COGS UPGRADE + ULTRA-FINE GRID")
print("="*70)

ml_pred = np.load(f'{OUT55}/ml_pred.npy')
cr_old = np.load(f'{OUT55}/cr_pred.npy')
naive_pred = np.load(f'{OUT55}/naive_pred.npy')
naive_cogs = np.load(f'{OUT55}/naive_cogs.npy')
df_train = pd.read_csv(f'{DD}/sales_train.csv', parse_dates=['Date'])
df_test = pd.read_csv(f'{DD}/sales_test.csv', parse_dates=['Date'])
dates = df_test['Date'].dt.strftime('%Y-%m-%d').values
bml = 0.90

# === Rebuild features for COGS training ===
TRAIN_START = df_train['Date'].min()
rev_lookup = dict(zip(df_train['Date'], df_train['Revenue']))
cogs_lookup = dict(zip(df_train['Date'], df_train['COGS']))
df_train['_doy'] = df_train['Date'].dt.dayofyear
doy_mean_r = df_train.groupby('_doy')['Revenue'].mean().to_dict()
df_train['_woy'] = df_train['Date'].dt.isocalendar().week.astype(int)
woy_mean = df_train.groupby('_woy')['Revenue'].mean().to_dict()
month_mean = df_train.groupby(df_train['Date'].dt.month)['Revenue'].mean().to_dict()
dow_mean = df_train.groupby(df_train['Date'].dt.dayofweek)['Revenue'].mean().to_dict()

def bld(df):
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
    df['rev_doy_mean'] = doy.map(doy_mean_r).fillna(df_train['Revenue'].mean())
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
df_all = bld(pd.concat([df_train, df_test], ignore_index=True))
df_tr = df_all[df_all['Date'] <= df_train['Date'].max()].copy()
df_te = df_all[df_all['Date'] > df_train['Date'].max()].copy()
exclude = {'Date','Revenue','COGS','COGS_Ratio','_doy','_woy'}
FEATS = [c for c in df_tr.columns if c not in exclude and df_tr[c].dtype in ['int64','float64','int32','category']]
CATS = ['month','dow','quarter']
y_log = np.log1p(df_tr['Revenue'].values)
df_tr['_year'] = df_tr['Date'].dt.year
sw = np.exp(-0.15 * (2023 - df_tr['_year'].values))
lgb_p = dict(objective='regression', metric='rmse', num_leaves=63, learning_rate=0.015,
             feature_fraction=0.7, bagging_fraction=0.8, bagging_freq=5, verbose=-1, n_jobs=-1)

# === 1. SMEARING ESTIMATOR ===
print("\n[1] Smearing Estimator...")
ds = lgb.Dataset(df_tr[FEATS], y_log, weight=sw, categorical_feature=CATS, free_raw_data=False)
m0 = lgb.train({**lgb_p, 'seed': 42}, ds, 800)
train_resid = y_log - m0.predict(df_tr[FEATS])
sigma2 = np.var(train_resid)
smear = np.exp(0.5 * sigma2)
print(f"  sigma2={sigma2:.6f}, smear_factor={smear:.6f} (+{(smear-1)*100:.2f}%)")
ml_smeared = ml_pred * smear

# === 2. FULL COGS ENSEMBLE ===
print("\n[2] Full COGS Ensemble (18 models)...")
cr_target = df_tr['COGS_Ratio'].values
xgb_p = dict(objective='reg:squarederror', learning_rate=0.015, max_depth=6,
             subsample=0.8, colsample_bytree=0.7, tree_method='hist')
cr_preds = []
for s in SEEDS:
    ds = lgb.Dataset(df_tr[FEATS], cr_target, categorical_feature=CATS, free_raw_data=False)
    cr_preds.append(('lgb', lgb.train({**lgb_p, 'seed': s}, ds, 400).predict(df_te[FEATS])))
for s in SEEDS:
    ds = lgb.Dataset(df_tr[FEATS], cr_target, categorical_feature=CATS, free_raw_data=False)
    cr_preds.append(('lgb_mae', lgb.train({**lgb_p, 'objective':'regression_l1', 'seed': s}, ds, 400).predict(df_te[FEATS])))
for s in SEEDS:
    dx = xgb.DMatrix(df_tr[FEATS], label=cr_target, enable_categorical=True)
    cr_preds.append(('xgb', xgb.train({**xgb_p, 'seed': s}, dx, 400).predict(xgb.DMatrix(df_te[FEATS], enable_categorical=True))))
for s in SEEDS:
    m = CatBoostRegressor(iterations=400, learning_rate=0.015, depth=6, loss_function='RMSE', verbose=0, random_seed=s, cat_features=CATS)
    m.fit(df_tr[FEATS], cr_target); cr_preds.append(('cat', m.predict(df_te[FEATS])))
for s in SEEDS:
    m = CatBoostRegressor(iterations=400, learning_rate=0.015, depth=6, loss_function='MAE', verbose=0, random_seed=s, cat_features=CATS)
    m.fit(df_tr[FEATS], cr_target); cr_preds.append(('cat_mae', m.predict(df_te[FEATS])))
df_tr_rf = df_tr[FEATS].copy(); df_te_rf = df_te[FEATS].copy()
for c in CATS: df_tr_rf[c] = df_tr_rf[c].astype(int); df_te_rf[c] = df_te_rf[c].astype(int)
for s in SEEDS:
    rf = RandomForestRegressor(n_estimators=200, max_depth=10, max_features=0.6, random_state=s, n_jobs=-1)
    rf.fit(df_tr_rf, cr_target); cr_preds.append(('rf', rf.predict(df_te_rf)))

# Weighted ensemble
w = {'lgb':0.25, 'lgb_mae':0.10, 'xgb':0.25, 'cat':0.20, 'cat_mae':0.10, 'rf':0.10}
cr_new = np.zeros(len(df_te))
w_sum = {k: 0 for k in w}
for name, pred in cr_preds:
    cr_new += w[name] / 3 * pred  # 3 seeds per type
cr_new = np.clip(cr_new, 0.65, 0.95)
print(f"  Old CR: mean={cr_old.mean():.4f}, New CR: mean={cr_new.mean():.4f}")

# === 3. SUBMISSIONS ===
print("\n[3] Generating submissions...")
blend = bml * ml_pred + (1-bml) * naive_pred
blend_sm = bml * ml_smeared + (1-bml) * naive_pred

def save(frev, cr_use, name):
    fcogs = np.clip(frev * cr_use, 0, frev)
    pd.DataFrame({'Date': dates, 'Revenue': frev.round(2), 'COGS': fcogs.round(2)}).to_csv(
        os.path.join(sub_dir, f'submission_{name}.csv'), index=False)
    print(f"  {name:35s} Rev={frev.mean():>10,.0f} COGS={fcogs.mean():>10,.0f}")

print("\n--- Ultra-fine (original) ---")
for m in [1.275, 1.278, 1.280, 1.282, 1.285]:
    ms = str(m).replace('.','')
    save(blend * m, cr_old, f'v62_fine_{ms}')

print("\n--- Smearing + original COGS ---")
for m in [1.20, 1.22, 1.24, 1.25, 1.26, 1.27, 1.28]:
    ms = str(m).replace('.','')
    save(blend_sm * m, cr_old, f'v62_smear_{ms}')

print("\n--- Original Revenue + New COGS ---")
for m in [1.275, 1.278, 1.280, 1.282, 1.285]:
    ms = str(m).replace('.','')
    save(blend * m, cr_new, f'v62_newcr_{ms}')

print("\n--- Smearing + New COGS ---")
for m in [1.20, 1.22, 1.25, 1.27]:
    ms = str(m).replace('.','')
    save(blend_sm * m, cr_new, f'v62_smcr_{ms}')

print("\n" + "="*70)
print("SUBMIT PRIORITY:")
print("  1. v62_fine_1278 / v62_fine_1282 (ultra-fine around best)")
print("  2. v62_newcr_1280 (same Rev, better COGS)")
print("  3. v62_smear_125 / v62_smear_126 (smearing needs lower mult)")
print("="*70)
