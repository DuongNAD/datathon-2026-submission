"""
train_v5.py — Datathon 2026 Forecasting Pipeline v5 ULTIMATE
=============================================================
Fixes applied vs v4:
  1. Full training data (2012-2022) with COVID weights
  2. Known-in-advance features ONLY (no data leakage)
  3. Event-aligned Tet lag (not static Lag-364)
  4. Leap year safe features
  5. Loss = RMSE (competition metric)
  6. COGS via Gross Margin % model (always COGS < Revenue)
  7. Real SHAP analysis
  8. Proper validation: hold-out 2021-07 -> 2022-12
  9. 5-seed ensemble for robustness
"""

import pandas as pd
import numpy as np
import holidays
import lightgbm as lgb
import joblib
import json
import shap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from datetime import date, timedelta
import warnings
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════
DATA_DIR   = 'dataset'
MODEL_DIR  = 'model_v5'
REPORT_DIR = 'reports'
SUBMISSION = 'submission_v5.csv'

VAL_START  = '2021-07-01'   # 18-month hold-out = same length as test
SEEDS      = [42, 123, 777, 2026, 314]
COVID_LOCKDOWN = [
    ('2020-03-22', '2020-04-22'),  # First lockdown
    ('2021-05-31', '2021-10-01'),  # Delta lockdown (strict)
]

import os
os.makedirs(MODEL_DIR, exist_ok=True)

# ═══════════════════════════════════════════════
# 1. LOAD DATA
# ═══════════════════════════════════════════════
print("=" * 60)
print("DATATHON 2026 — FORECASTING PIPELINE v5 ULTIMATE")
print("=" * 60)

df_train = pd.read_csv(f'{DATA_DIR}/sales_train.csv', parse_dates=['Date'])
df_test  = pd.read_csv(f'{DATA_DIR}/sales_test.csv',  parse_dates=['Date'])

print(f"Train: {df_train['Date'].min().date()} -> {df_train['Date'].max().date()} ({len(df_train)} days)")
print(f"Test:  {df_test['Date'].min().date()} -> {df_test['Date'].max().date()} ({len(df_test)} days)")

# Gross Margin %
df_train['GM_pct'] = (df_train['Revenue'] - df_train['COGS']) / df_train['Revenue']

# ═══════════════════════════════════════════════
# 2. FEATURE ENGINEERING (Known-in-advance ONLY)
# ═══════════════════════════════════════════════
print("\n[1/6] Feature Engineering...")

# --- Vietnamese holidays & Tet ---
def get_tet_dates(year_range):
    """Extract Tet dates from holidays library."""
    vn = holidays.VN(years=year_range)
    tet_kw = ['Tết Nguyên Đán', 'Giao thừa', 'Tết', 'Mùng']
    tet_dates = sorted([
        d for d, name in vn.items()
        if any(kw in name for kw in tet_kw)
    ])
    return tet_dates

TET_DATES = get_tet_dates(range(2011, 2026))

# Pre-compute Tet "peaks" = first day of Tet each year
def get_tet_peak_by_year(tet_dates):
    """Get the primary Tet date for each year."""
    peaks = {}
    for d in tet_dates:
        y = d.year
        if y not in peaks or d < peaks[y]:
            peaks[y] = d
    return peaks

TET_PEAKS = get_tet_peak_by_year(TET_DATES)

def add_features(df, train_df=None):
    """Add all known-in-advance features. No data leakage."""
    df = df.copy()
    d = df['Date']

    # --- Calendar ---
    df['year']  = d.dt.year
    df['month'] = d.dt.month
    df['day']   = d.dt.day
    df['day_of_week'] = d.dt.dayofweek
    df['quarter'] = d.dt.quarter
    df['day_of_year'] = d.dt.dayofyear
    df['week_of_year'] = d.dt.isocalendar().week.astype(int)
    df['week_of_month'] = (d.dt.day - 1) // 7 + 1

    # --- Flags ---
    df['is_weekend']     = df['day_of_week'].isin([5, 6]).astype(int)
    df['is_month_start'] = d.dt.is_month_start.astype(int)
    df['is_month_end']   = d.dt.is_month_end.astype(int)
    df['is_payday']      = df['day'].isin([1, 15]).astype(int)
    df['is_year_start']  = ((df['month'] == 1) & (df['day'] <= 7)).astype(int)
    df['is_year_end']    = ((df['month'] == 12) & (df['day'] >= 25)).astype(int)

    # --- Cyclic encoding (leap-year safe: use month+dow, not dayofyear) ---
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    df['dow_sin']   = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['dow_cos']   = np.cos(2 * np.pi * df['day_of_week'] / 7)
    # Fourier terms for sub-annual seasonality (use day/365.25 for leap-safe)
    frac_year = (df['day_of_year'] - 1) / 365.25
    for k in [1, 2, 3, 4]:
        df[f'fourier_sin_{k}'] = np.sin(2 * np.pi * k * frac_year)
        df[f'fourier_cos_{k}'] = np.cos(2 * np.pi * k * frac_year)

    # --- Tet Lunar New Year ---
    tet_set = set(TET_DATES)
    df['is_tet'] = d.dt.date.apply(lambda x: 1 if x in tet_set else 0)

    def days_to_next_tet(dt):
        future = [t for t in TET_DATES if t >= dt.date()]
        return (future[0] - dt.date()).days if future else 365
    df['days_to_tet'] = d.apply(days_to_next_tet)
    df['is_approaching_tet'] = (df['days_to_tet'] <= 21).astype(int)

    def days_since_last_tet(dt):
        past = [t for t in TET_DATES if t <= dt.date()]
        return (dt.date() - past[-1]).days if past else 365
    df['days_since_tet'] = d.apply(days_since_last_tet)

    # --- All VN public holidays ---
    vn_holidays = holidays.VN(years=range(2011, 2026))
    all_holidays = set(vn_holidays.keys())
    df['is_public_holiday'] = d.dt.date.apply(lambda x: 1 if x in all_holidays else 0)

    def days_to_next_holiday(dt):
        future = sorted([h for h in all_holidays if h >= dt.date()])
        return (future[0] - dt.date()).days if future else 365
    df['days_to_holiday'] = d.apply(days_to_next_holiday)

    # --- Mega Sale Events (deterministic calendar) ---
    def is_mega_sale(dt):
        m, day = dt.month, dt.day
        # Valentine, Women's Day, Reunification, Labor, National Day,
        # 9/9, 10/10, 11/11, 12/12, Black Friday (last Fri of Nov)
        fixed = [(2,14),(3,8),(4,30),(5,1),(9,2),(9,9),(10,10),(10,20),(11,11),(12,12)]
        if (m, day) in fixed:
            return 1
        # Black Friday: last Friday of November
        if m == 11 and day >= 20 and day <= 30 and dt.dayofweek == 4:
            return 1
        return 0
    df['is_mega_sale'] = d.apply(is_mega_sale)

    # --- COVID lockdown flag ---
    def is_covid(dt):
        for start, end in COVID_LOCKDOWN:
            if pd.Timestamp(start) <= dt <= pd.Timestamp(end):
                return 1
        return 0
    df['is_covid_lockdown'] = d.apply(is_covid)

    # --- Event-aligned Tet lag ---
    # Revenue on "same day relative to Tet" last year
    if train_df is not None:
        train_lookup = train_df.set_index('Date')['Revenue'].to_dict()
        def tet_aligned_lag(dt):
            yr = dt.year
            # Find Tet peak for this year and last year
            tet_this = TET_PEAKS.get(yr)
            tet_last = TET_PEAKS.get(yr - 1)
            if tet_this is None or tet_last is None:
                return np.nan
            offset = (dt.date() - tet_this).days
            aligned_date = pd.Timestamp(tet_last + timedelta(days=offset))
            return train_lookup.get(aligned_date, np.nan)
        df['revenue_tet_aligned_lag'] = d.apply(tet_aligned_lag)
        # Also standard Lag-364 (same weekday last year)
        def lag_364(dt):
            return train_lookup.get(dt - pd.Timedelta(days=364), np.nan)
        df['revenue_lag_364'] = d.apply(lag_364)
    else:
        df['revenue_tet_aligned_lag'] = np.nan
        df['revenue_lag_364'] = np.nan

    # --- Trend index ---
    base = pd.Timestamp('2012-07-04')
    df['time_idx'] = (d - base).dt.days

    # --- Categoricals ---
    for col in ['month', 'day_of_week', 'quarter']:
        df[col] = df[col].astype('category')

    return df

# Build features
df_train = add_features(df_train, train_df=df_train)
df_test  = add_features(df_test,  train_df=df_train)

# ═══════════════════════════════════════════════
# 3. DEFINE FEATURES
# ═══════════════════════════════════════════════
FEATURES = [
    'time_idx',
    'month', 'day', 'day_of_week', 'quarter', 'day_of_year',
    'week_of_year', 'week_of_month',
    'is_weekend', 'is_month_start', 'is_month_end',
    'is_payday', 'is_year_start', 'is_year_end',
    'month_sin', 'month_cos', 'dow_sin', 'dow_cos',
    'fourier_sin_1', 'fourier_cos_1',
    'fourier_sin_2', 'fourier_cos_2',
    'fourier_sin_3', 'fourier_cos_3',
    'fourier_sin_4', 'fourier_cos_4',
    'is_mega_sale', 'is_tet', 'days_to_tet', 'is_approaching_tet',
    'days_since_tet', 'is_public_holiday', 'days_to_holiday',
    'is_covid_lockdown',
    'revenue_tet_aligned_lag', 'revenue_lag_364',
]
CATEGORICALS = ['month', 'day_of_week', 'quarter']

# Fill NaN in lag features with median
for col in ['revenue_tet_aligned_lag', 'revenue_lag_364']:
    med = df_train[col].median()
    df_train[col] = df_train[col].fillna(med)
    df_test[col]  = df_test[col].fillna(med)

print(f"  Total features: {len(FEATURES)}")
print(f"  Lag features NaN filled with median")

# ═══════════════════════════════════════════════
# 4. TRAIN/VAL SPLIT + SAMPLE WEIGHTS
# ═══════════════════════════════════════════════
print("\n[2/6] Train/Validation split...")

mask_val   = df_train['Date'] >= VAL_START
df_tr = df_train[~mask_val].copy()
df_vl = df_train[mask_val].copy()

print(f"  Train: {df_tr['Date'].min().date()} -> {df_tr['Date'].max().date()} ({len(df_tr)} days)")
print(f"  Val:   {df_vl['Date'].min().date()} -> {df_vl['Date'].max().date()} ({len(df_vl)} days)")

# Sample weights: downweight COVID lockdown periods
df_tr['weight'] = 1.0
df_tr.loc[df_tr['is_covid_lockdown'] == 1, 'weight'] = 0.3

# ═══════════════════════════════════════════════
# 5. TRAIN REVENUE MODEL (Direct LightGBM — no trend decomposition)
# ═══════════════════════════════════════════════
print("\n[3/6] Training Revenue model (direct)...")

# Floor = minimum daily revenue in training (avoid predicting 0)
REV_FLOOR = df_tr['Revenue'].quantile(0.01)
print(f"  Revenue floor (1st percentile): {REV_FLOOR:,.0f}")

lgb_params = {
    'objective':     'regression',
    'metric':        'rmse',
    'boosting_type': 'gbdt',
    'num_leaves':    127,
    'learning_rate': 0.03,
    'feature_fraction': 0.8,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'min_child_samples': 20,
    'reg_alpha': 0.1,
    'reg_lambda': 1.0,
    'verbose': -1,
    'n_jobs': -1,
}

boosters = []
for i, seed in enumerate(SEEDS):
    params = {**lgb_params, 'seed': seed, 'bagging_seed': seed}
    ds_tr = lgb.Dataset(
        df_tr[FEATURES], df_tr['Revenue'].values,
        weight=df_tr['weight'].values,
        categorical_feature=CATEGORICALS,
        free_raw_data=False
    )
    ds_vl = lgb.Dataset(
        df_vl[FEATURES], df_vl['Revenue'].values,
        categorical_feature=CATEGORICALS,
        free_raw_data=False
    )
    bst = lgb.train(
        params, ds_tr,
        num_boost_round=3000,
        valid_sets=[ds_vl],
        callbacks=[lgb.early_stopping(100, verbose=False)]
    )
    boosters.append(bst)
    print(f"  Seed {seed}: best_iter={bst.best_iteration}")

# Ensemble prediction
def predict_revenue(df_feat, boosters, floor=0):
    preds = np.column_stack([
        bst.predict(df_feat[FEATURES]) for bst in boosters
    ])
    return np.maximum(floor, preds.mean(axis=1))

rev_val_pred = predict_revenue(df_vl, boosters, floor=REV_FLOOR)

# ═══════════════════════════════════════════════
# 6. TRAIN GROSS MARGIN % MODEL
# ═══════════════════════════════════════════════
print("\n[4/6] Training Gross Margin % model...")

# GM% features (same calendar features, no lag needed for margin)
GM_FEATURES = [f for f in FEATURES if 'revenue_' not in f]

gm_params = {
    'objective': 'regression',
    'metric': 'rmse',
    'boosting_type': 'gbdt',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.8,
    'verbose': -1,
}

gm_boosters = []
for seed in SEEDS:
    params = {**gm_params, 'seed': seed}
    ds_tr = lgb.Dataset(
        df_tr[GM_FEATURES], df_tr['GM_pct'].values,
        weight=df_tr['weight'].values,
        categorical_feature=CATEGORICALS,
        free_raw_data=False
    )
    ds_vl = lgb.Dataset(
        df_vl[GM_FEATURES], df_vl['GM_pct'].values,
        categorical_feature=CATEGORICALS,
        free_raw_data=False
    )
    bst = lgb.train(
        params, ds_tr,
        num_boost_round=1000,
        valid_sets=[ds_vl],
        callbacks=[lgb.early_stopping(50, verbose=False)]
    )
    gm_boosters.append(bst)

def predict_gm(df_feat, gm_boosters):
    preds = np.column_stack([
        bst.predict(df_feat[GM_FEATURES]) for bst in gm_boosters
    ])
    gm = preds.mean(axis=1)
    # Clamp: GM% must be between 0.01 and 0.50 (realistic range)
    return np.clip(gm, 0.01, 0.50)

gm_val_pred = predict_gm(df_vl, gm_boosters)
cogs_val_pred = rev_val_pred * (1 - gm_val_pred)

print(f"  GM% model trained (5 seeds)")
print(f"  GM% val range: [{gm_val_pred.min():.4f}, {gm_val_pred.max():.4f}]")
print(f"  COGS > Revenue violations: {(cogs_val_pred > rev_val_pred).sum()} ✅")

# ═══════════════════════════════════════════════
# 7. VALIDATION METRICS
# ═══════════════════════════════════════════════
print("\n[5/6] Validation Results (2021-07 → 2022-12)...")

actual_rev  = df_vl['Revenue'].values
actual_cogs = df_vl['COGS'].values

rev_mae  = mean_absolute_error(actual_rev, rev_val_pred)
rev_rmse = np.sqrt(mean_squared_error(actual_rev, rev_val_pred))
rev_r2   = r2_score(actual_rev, rev_val_pred)
rev_mape = np.mean(np.abs((actual_rev - rev_val_pred) / actual_rev)) * 100

cogs_mae  = mean_absolute_error(actual_cogs, cogs_val_pred)
cogs_rmse = np.sqrt(mean_squared_error(actual_cogs, cogs_val_pred))

print(f"\n  ┌──────────────────────────────────────┐")
print(f"  │  REVENUE VALIDATION                   │")
print(f"  │  MAE:   {rev_mae:>12,.0f}                │")
print(f"  │  RMSE:  {rev_rmse:>12,.0f}                │")
print(f"  │  R²:    {rev_r2:>12.4f}                │")
print(f"  │  MAPE:  {rev_mape:>11.2f}%                │")
print(f"  ├──────────────────────────────────────┤")
print(f"  │  COGS VALIDATION                      │")
print(f"  │  MAE:   {cogs_mae:>12,.0f}                │")
print(f"  │  RMSE:  {cogs_rmse:>12,.0f}                │")
print(f"  └──────────────────────────────────────┘")

# Per-year breakdown
for y in df_vl['year'].unique():
    m = df_vl['year'] == y
    r2_y = r2_score(actual_rev[m], rev_val_pred[m])
    mape_y = np.mean(np.abs((actual_rev[m] - rev_val_pred[m]) / actual_rev[m])) * 100
    print(f"  Year {y}: R²={r2_y:.4f} | MAPE={mape_y:.1f}%")

# ═══════════════════════════════════════════════
# 8. RETRAIN ON FULL DATA + PREDICT TEST
# ═══════════════════════════════════════════════
print("\n[6/6] Retrain on full data + generate submission...")

# Retrain trend — not needed for direct model
df_train['weight'] = 1.0
df_train.loc[df_train['is_covid_lockdown'] == 1, 'weight'] = 0.3

# Retrain LightGBM ensemble on full data
avg_best_iter = int(np.mean([b.best_iteration for b in boosters]) * 1.1)
retrain_rounds = max(avg_best_iter, 200)
print(f"  Retrain rounds (revenue): {retrain_rounds}")

final_boosters = []
for seed in SEEDS:
    params = {**lgb_params, 'seed': seed, 'bagging_seed': seed}
    ds = lgb.Dataset(
        df_train[FEATURES], df_train['Revenue'].values,
        weight=df_train['weight'].values,
        categorical_feature=CATEGORICALS,
        free_raw_data=False
    )
    bst = lgb.train(params, ds, num_boost_round=retrain_rounds)
    final_boosters.append(bst)

# Retrain GM% ensemble
final_gm_boosters = []
for seed in SEEDS:
    params = {**gm_params, 'seed': seed}
    ds = lgb.Dataset(
        df_train[GM_FEATURES], df_train['GM_pct'].values,
        weight=df_train['weight'].values,
        categorical_feature=CATEGORICALS,
        free_raw_data=False
    )
    bst = lgb.train(params, ds, num_boost_round=500)
    final_gm_boosters.append(bst)

# Predict test
rev_test = predict_revenue(df_test, final_boosters, floor=REV_FLOOR)
gm_test  = predict_gm(df_test, final_gm_boosters)
cogs_test = rev_test * (1 - gm_test)

# ═══════════════════════════════════════════════
# 9. SANITY CHECKS
# ═══════════════════════════════════════════════
print("\n  Sanity Checks:")
print(f"  Negative Revenue: {(rev_test < 0).sum()}")
print(f"  COGS > Revenue:   {(cogs_test > rev_test).sum()}")
print(f"  Min Revenue:      {rev_test.min():,.0f}")
print(f"  Max Revenue:      {rev_test.max():,.0f}")
print(f"  Mean Revenue:     {rev_test.mean():,.0f}")

m23 = df_test['year'] == 2023
m24 = df_test['year'] == 2024
mean_23 = rev_test[m23].mean()
mean_24 = rev_test[m24].mean()
growth  = (mean_24 / mean_23 - 1) * 100
print(f"  Mean 2023:        {mean_23:,.0f}")
print(f"  Mean 2024:        {mean_24:,.0f}")
print(f"  Growth 2024/2023: {growth:+.1f}%")
print(f"  GM% test range:   [{gm_test.min():.4f}, {gm_test.max():.4f}]")

# ═══════════════════════════════════════════════
# 10. SAVE SUBMISSION + ARTIFACTS
# ═══════════════════════════════════════════════
submission = pd.DataFrame({
    'Date': df_test['Date'].dt.strftime('%Y-%m-%d'),
    'Revenue': rev_test.round(2),
    'COGS': cogs_test.round(2)
})
submission.to_csv(SUBMISSION, index=False)
print(f"\n  ✅ Saved {SUBMISSION} ({len(submission)} rows)")

# Save model artifacts
for i, bst in enumerate(final_boosters):
    bst.save_model(f'{MODEL_DIR}/lgbm_rev_seed{SEEDS[i]}.txt')
for i, bst in enumerate(final_gm_boosters):
    bst.save_model(f'{MODEL_DIR}/lgbm_gm_seed{SEEDS[i]}.txt')

# Save features list
with open(f'{MODEL_DIR}/features.json', 'w') as f:
    json.dump({
        'revenue_features': FEATURES,
        'gm_features': GM_FEATURES,
        'categoricals': CATEGORICALS
    }, f, indent=2)

# Save validation metrics
metrics = {
    'version': 'v5_ultimate',
    'val_period': f'{VAL_START} → 2022-12-31',
    'ensemble_seeds': SEEDS,
    'revenue': {
        'mae': float(rev_mae), 'rmse': float(rev_rmse),
        'r2': float(rev_r2), 'mape': float(rev_mape)
    },
    'cogs': {
        'mae': float(cogs_mae), 'rmse': float(cogs_rmse)
    },
    'sanity': {
        'neg_revenue': int((rev_test < 0).sum()),
        'cogs_gt_revenue': int((cogs_test > rev_test).sum()),
        'mean_2023': float(mean_23),
        'mean_2024': float(mean_24),
        'growth_pct': float(growth)
    }
}
with open(f'{MODEL_DIR}/validation_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

# ═══════════════════════════════════════════════
# 11. REAL SHAP ANALYSIS
# ═══════════════════════════════════════════════
print("\n  Generating REAL SHAP analysis...")
try:
    # Re-train a single booster WITHOUT categorical_feature for SHAP compatibility
    shap_params = {**lgb_params, 'seed': 42, 'bagging_seed': 42}
    X_shap_train = df_tr[FEATURES].copy()
    X_shap_val = df_vl[FEATURES].copy()
    for col in CATEGORICALS:
        X_shap_train[col] = X_shap_train[col].astype(int)
        X_shap_val[col] = X_shap_val[col].astype(int)
    
    ds_shap = lgb.Dataset(X_shap_train, df_tr['Revenue'].values, weight=df_tr['weight'].values, free_raw_data=False)
    ds_shap_val = lgb.Dataset(X_shap_val, df_vl['Revenue'].values, free_raw_data=False)
    shap_bst = lgb.train(
        shap_params, ds_shap,
        num_boost_round=2000,
        valid_sets=[ds_shap_val],
        callbacks=[lgb.early_stopping(50, verbose=False)]
    )
    
    explainer = shap.TreeExplainer(shap_bst)
    shap_values = explainer.shap_values(X_shap_val)

    # Save SHAP summary plot (beeswarm)
    plt.figure(figsize=(12, 8))
    shap.summary_plot(shap_values, X_shap_val, show=False, max_display=15)
    plt.title('SHAP Feature Importances - LightGBM Revenue Model (v5)', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'{MODEL_DIR}/shap_summary_real.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  SHAP beeswarm plot saved")

    # Bar plot
    plt.figure(figsize=(10, 7))
    shap.summary_plot(shap_values, X_shap_val, plot_type='bar', show=False, max_display=15)
    plt.title('Mean |SHAP| - Feature Importance (v5)', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'{MODEL_DIR}/shap_bar_real.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  SHAP bar plot saved")

    # Top features
    mean_shap = np.abs(shap_values).mean(axis=0)
    feat_importance = sorted(zip(FEATURES, mean_shap), key=lambda x: -x[1])
    print("\n  Top 10 Features by mean |SHAP|:")
    for i, (f, v) in enumerate(feat_importance[:10]):
        print(f"    {i+1}. {f}: {v:,.0f}")

    with open(f'{MODEL_DIR}/shap_importances.json', 'w') as f:
        json.dump({feat: float(val) for feat, val in feat_importance}, f, indent=2)

except Exception as e:
    print(f"  SHAP failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("PIPELINE COMPLETE!")
print("=" * 60)
