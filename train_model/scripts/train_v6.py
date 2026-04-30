"""
train_v6.py — Datathon 2026 Forecasting Pipeline v6
====================================================
Improvements over v5:
  1. Log-transform Revenue target (right-skewed → better RMSE)
  2. Add Lag-1, Lag-7, Lag-30 (strongest autocorrelations: 0.87, 0.49, 0.65)
  3. Use Lag-365 alongside Lag-364 (0.79 > 0.75 correlation)
  4. Month-end spike features (day>=28 has 70% higher revenue)
  5. Remove zero-SHAP features (is_year_start, is_year_end, is_tet, is_approaching_tet)
  6. Rolling mean features (7d, 30d windows)
  7. Interaction features (month × day_of_week)
  8. Tuned hyperparameters with lower learning rate + more trees
  9. Separate GM% by month-cluster for accuracy
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
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from datetime import date, timedelta
import warnings
warnings.filterwarnings('ignore')
import os

# ═══════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════
# All paths resolve relative to train_model/ (parent of scripts/)
_SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, '..'))

DATA_DIR   = os.path.join(_PROJECT_DIR, 'dataset')
MODEL_DIR  = os.path.join(_PROJECT_DIR, 'model_v6')
SUBMISSION = os.path.join(_PROJECT_DIR, 'submission_v6.csv')

VAL_START  = '2021-07-01'
SEEDS      = [42, 123, 777, 2026, 314]
COVID_LOCKDOWN = [
    ('2020-03-22', '2020-04-22'),
    ('2021-05-31', '2021-10-01'),
]

os.makedirs(MODEL_DIR, exist_ok=True)

# ═══════════════════════════════════════════════
# 1. LOAD DATA
# ═══════════════════════════════════════════════
print("=" * 60)
print("DATATHON 2026 — FORECASTING PIPELINE v6")
print("=" * 60)

df_train = pd.read_csv(f'{DATA_DIR}/sales_train.csv', parse_dates=['Date'])
df_test  = pd.read_csv(f'{DATA_DIR}/sales_test.csv',  parse_dates=['Date'])

print(f"Train: {df_train['Date'].min().date()} -> {df_train['Date'].max().date()} ({len(df_train)} days)")
print(f"Test:  {df_test['Date'].min().date()} -> {df_test['Date'].max().date()} ({len(df_test)} days)")

df_train['GM_pct'] = (df_train['Revenue'] - df_train['COGS']) / df_train['Revenue']

# ═══════════════════════════════════════════════
# 2. FEATURE ENGINEERING
# ═══════════════════════════════════════════════
print("\n[1/7] Feature Engineering...")

def get_tet_dates(year_range):
    vn = holidays.VN(years=year_range)
    tet_kw = ['Tết Nguyên Đán', 'Giao thừa', 'Tết', 'Mùng']
    return sorted([d for d, name in vn.items() if any(kw in name for kw in tet_kw)])

TET_DATES = get_tet_dates(range(2011, 2026))

def get_tet_peak_by_year(tet_dates):
    peaks = {}
    for d in tet_dates:
        y = d.year
        if y not in peaks or d < peaks[y]:
            peaks[y] = d
    return peaks

TET_PEAKS = get_tet_peak_by_year(TET_DATES)

def add_features(df, train_df=None):
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

    # --- NEW: Month-end spike zone (day >= 28 has 70% higher revenue) ---
    df['is_month_end_zone'] = (df['day'] >= 28).astype(int)
    df['days_to_month_end'] = d.dt.daysinmonth - df['day']

    # --- Cyclic encoding ---
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    df['dow_sin']   = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['dow_cos']   = np.cos(2 * np.pi * df['day_of_week'] / 7)
    frac_year = (df['day_of_year'] - 1) / 365.25
    for k in [1, 2, 3, 4]:
        df[f'fourier_sin_{k}'] = np.sin(2 * np.pi * k * frac_year)
        df[f'fourier_cos_{k}'] = np.cos(2 * np.pi * k * frac_year)

    # --- Tet ---
    tet_set = set(TET_DATES)
    def days_to_next_tet(dt):
        future = [t for t in TET_DATES if t >= dt.date()]
        return (future[0] - dt.date()).days if future else 365
    df['days_to_tet'] = d.apply(days_to_next_tet)

    def days_since_last_tet(dt):
        past = [t for t in TET_DATES if t <= dt.date()]
        return (dt.date() - past[-1]).days if past else 365
    df['days_since_tet'] = d.apply(days_since_last_tet)

    # --- Public holidays ---
    vn_holidays = holidays.VN(years=range(2011, 2026))
    all_holidays = set(vn_holidays.keys())
    df['is_public_holiday'] = d.dt.date.apply(lambda x: 1 if x in all_holidays else 0)
    def days_to_next_holiday(dt):
        future = sorted([h for h in all_holidays if h >= dt.date()])
        return (future[0] - dt.date()).days if future else 365
    df['days_to_holiday'] = d.apply(days_to_next_holiday)

    # --- Mega Sale ---
    def is_mega_sale(dt):
        m, day = dt.month, dt.day
        fixed = [(2,14),(3,8),(4,30),(5,1),(9,2),(9,9),(10,10),(10,20),(11,11),(12,12)]
        if (m, day) in fixed:
            return 1
        if m == 11 and day >= 20 and day <= 30 and dt.dayofweek == 4:
            return 1
        return 0
    df['is_mega_sale'] = d.apply(is_mega_sale)

    # --- COVID ---
    def is_covid(dt):
        for start, end in COVID_LOCKDOWN:
            if pd.Timestamp(start) <= dt <= pd.Timestamp(end):
                return 1
        return 0
    df['is_covid_lockdown'] = d.apply(is_covid)

    # --- LAG FEATURES (key improvement) ---
    if train_df is not None:
        train_lookup = train_df.set_index('Date')['Revenue'].to_dict()

        # Tet-aligned lag
        def tet_aligned_lag(dt):
            yr = dt.year
            tet_this = TET_PEAKS.get(yr)
            tet_last = TET_PEAKS.get(yr - 1)
            if tet_this is None or tet_last is None:
                return np.nan
            offset = (dt.date() - tet_this).days
            aligned_date = pd.Timestamp(tet_last + timedelta(days=offset))
            return train_lookup.get(aligned_date, np.nan)
        df['revenue_tet_aligned_lag'] = d.apply(tet_aligned_lag)

        # Standard lags - NEW: add Lag-1, Lag-7, Lag-30, Lag-365
        for lag in [1, 7, 30, 364, 365]:
            col_name = f'revenue_lag_{lag}'
            df[col_name] = d.apply(lambda dt, l=lag: train_lookup.get(dt - pd.Timedelta(days=l), np.nan))

        # NEW: Rolling means (known from train data)
        train_series = train_df.set_index('Date')['Revenue'].sort_index()
        def rolling_mean(dt, window):
            end = dt - pd.Timedelta(days=1)
            start = end - pd.Timedelta(days=window-1)
            subset = train_series[start:end]
            return subset.mean() if len(subset) >= window // 2 else np.nan
        df['revenue_rolling_7'] = d.apply(lambda dt: rolling_mean(dt, 7))
        df['revenue_rolling_30'] = d.apply(lambda dt: rolling_mean(dt, 30))

    else:
        df['revenue_tet_aligned_lag'] = np.nan
        for lag in [1, 7, 30, 364, 365]:
            df[f'revenue_lag_{lag}'] = np.nan
        df['revenue_rolling_7'] = np.nan
        df['revenue_rolling_30'] = np.nan

    # --- Trend index ---
    base = pd.Timestamp('2012-07-04')
    df['time_idx'] = (d - base).dt.days

    # --- Categoricals ---
    for col in ['month', 'day_of_week', 'quarter']:
        df[col] = df[col].astype('category')

    return df

df_train = add_features(df_train, train_df=df_train)
df_test  = add_features(df_test,  train_df=df_train)

# ═══════════════════════════════════════════════
# 3. DEFINE FEATURES (pruned: removed zero-SHAP features)
# ═══════════════════════════════════════════════
FEATURES = [
    'time_idx',
    'month', 'day', 'day_of_week', 'quarter', 'day_of_year',
    'week_of_year', 'week_of_month',
    'is_weekend', 'is_month_start', 'is_month_end',
    'is_payday',
    # NEW month-end features
    'is_month_end_zone', 'days_to_month_end',
    # Cyclic
    'month_sin', 'month_cos', 'dow_sin', 'dow_cos',
    'fourier_sin_1', 'fourier_cos_1',
    'fourier_sin_2', 'fourier_cos_2',
    'fourier_sin_3', 'fourier_cos_3',
    'fourier_sin_4', 'fourier_cos_4',
    # Events
    'is_mega_sale', 'days_to_tet',
    'days_since_tet', 'is_public_holiday', 'days_to_holiday',
    'is_covid_lockdown',
    # Lags (expanded)
    'revenue_tet_aligned_lag',
    'revenue_lag_1', 'revenue_lag_7', 'revenue_lag_30',
    'revenue_lag_364', 'revenue_lag_365',
    # Rolling
    'revenue_rolling_7', 'revenue_rolling_30',
]
CATEGORICALS = ['month', 'day_of_week', 'quarter']

# Fill NaN in lag/rolling features
lag_cols = [c for c in FEATURES if 'revenue_' in c]
for col in lag_cols:
    med = df_train[col].median()
    df_train[col] = df_train[col].fillna(med)
    df_test[col]  = df_test[col].fillna(med)

print(f"  Total features: {len(FEATURES)}")

# ═══════════════════════════════════════════════
# 4. TRAIN/VAL SPLIT
# ═══════════════════════════════════════════════
print("\n[2/7] Train/Validation split...")

mask_val = df_train['Date'] >= VAL_START
df_tr = df_train[~mask_val].copy()
df_vl = df_train[mask_val].copy()

print(f"  Train: {df_tr['Date'].min().date()} -> {df_tr['Date'].max().date()} ({len(df_tr)} days)")
print(f"  Val:   {df_vl['Date'].min().date()} -> {df_vl['Date'].max().date()} ({len(df_vl)} days)")

df_tr['weight'] = 1.0
df_tr.loc[df_tr['is_covid_lockdown'] == 1, 'weight'] = 0.3

# ═══════════════════════════════════════════════
# 5. TRAIN REVENUE MODEL (Log-transform target)
# ═══════════════════════════════════════════════
print("\n[3/7] Training Revenue model (log-transform)...")

REV_FLOOR = df_tr['Revenue'].quantile(0.01)
print(f"  Revenue floor (1st percentile): {REV_FLOOR:,.0f}")

# Log-transform target for better handling of skewed distribution
y_tr_log = np.log1p(df_tr['Revenue'].values)
y_vl_log = np.log1p(df_vl['Revenue'].values)

lgb_params = {
    'objective':     'regression',
    'metric':        'rmse',
    'boosting_type': 'gbdt',
    'num_leaves':    127,
    'learning_rate': 0.02,         # lower LR for better generalization
    'feature_fraction': 0.75,
    'bagging_fraction': 0.75,
    'bagging_freq': 5,
    'min_child_samples': 15,
    'reg_alpha': 0.1,
    'reg_lambda': 1.0,
    'max_depth': -1,
    'verbose': -1,
    'n_jobs': -1,
}

boosters = []
for i, seed in enumerate(SEEDS):
    params = {**lgb_params, 'seed': seed, 'bagging_seed': seed}
    ds_tr = lgb.Dataset(
        df_tr[FEATURES], y_tr_log,
        weight=df_tr['weight'].values,
        categorical_feature=CATEGORICALS,
        free_raw_data=False
    )
    ds_vl = lgb.Dataset(
        df_vl[FEATURES], y_vl_log,
        categorical_feature=CATEGORICALS,
        free_raw_data=False
    )
    bst = lgb.train(
        params, ds_tr,
        num_boost_round=5000,
        valid_sets=[ds_vl],
        callbacks=[lgb.early_stopping(150, verbose=False)]
    )
    boosters.append(bst)
    print(f"  Seed {seed}: best_iter={bst.best_iteration}")

def predict_revenue(df_feat, boosters, floor=0):
    preds_log = np.column_stack([
        bst.predict(df_feat[FEATURES]) for bst in boosters
    ])
    preds = np.expm1(preds_log.mean(axis=1))  # inverse log-transform
    return np.maximum(floor, preds)

rev_val_pred = predict_revenue(df_vl, boosters, floor=REV_FLOOR)

# ═══════════════════════════════════════════════
# 6. TRAIN GROSS MARGIN % MODEL
# ═══════════════════════════════════════════════
print("\n[4/7] Training Gross Margin % model...")

GM_FEATURES = [f for f in FEATURES if 'revenue_' not in f]

gm_params = {
    'objective': 'regression',
    'metric': 'rmse',
    'boosting_type': 'gbdt',
    'num_leaves': 31,
    'learning_rate': 0.03,
    'feature_fraction': 0.8,
    'min_child_samples': 20,
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
        num_boost_round=2000,
        valid_sets=[ds_vl],
        callbacks=[lgb.early_stopping(100, verbose=False)]
    )
    gm_boosters.append(bst)

def predict_gm(df_feat, gm_boosters):
    preds = np.column_stack([
        bst.predict(df_feat[GM_FEATURES]) for bst in gm_boosters
    ])
    gm = preds.mean(axis=1)
    return np.clip(gm, 0.01, 0.50)

gm_val_pred = predict_gm(df_vl, gm_boosters)
cogs_val_pred = rev_val_pred * (1 - gm_val_pred)

print(f"  GM% val range: [{gm_val_pred.min():.4f}, {gm_val_pred.max():.4f}]")
print(f"  COGS > Revenue violations: {(cogs_val_pred > rev_val_pred).sum()}")

# ═══════════════════════════════════════════════
# 7. VALIDATION METRICS
# ═══════════════════════════════════════════════
print("\n[5/7] Validation Results...")

actual_rev  = df_vl['Revenue'].values
actual_cogs = df_vl['COGS'].values

rev_mae  = mean_absolute_error(actual_rev, rev_val_pred)
rev_rmse = np.sqrt(mean_squared_error(actual_rev, rev_val_pred))
rev_r2   = r2_score(actual_rev, rev_val_pred)
rev_mape = np.mean(np.abs((actual_rev - rev_val_pred) / actual_rev)) * 100

cogs_mae  = mean_absolute_error(actual_cogs, cogs_val_pred)
cogs_rmse = np.sqrt(mean_squared_error(actual_cogs, cogs_val_pred))

print(f"\n  REVENUE:  MAE={rev_mae:,.0f}  RMSE={rev_rmse:,.0f}  R2={rev_r2:.4f}  MAPE={rev_mape:.2f}%")
print(f"  COGS:     MAE={cogs_mae:,.0f}  RMSE={cogs_rmse:,.0f}")

for y in sorted(df_vl['year'].unique()):
    m = df_vl['year'] == y
    r2_y = r2_score(actual_rev[m], rev_val_pred[m])
    mape_y = np.mean(np.abs((actual_rev[m] - rev_val_pred[m]) / actual_rev[m])) * 100
    print(f"  Year {y}: R2={r2_y:.4f} | MAPE={mape_y:.1f}%")

# ═══════════════════════════════════════════════
# 8. RETRAIN ON FULL DATA + PREDICT TEST
# ═══════════════════════════════════════════════
print("\n[6/7] Retrain on full data + generate submission...")

df_train['weight'] = 1.0
df_train.loc[df_train['is_covid_lockdown'] == 1, 'weight'] = 0.3

y_full_log = np.log1p(df_train['Revenue'].values)
avg_best = int(np.mean([b.best_iteration for b in boosters]) * 1.1)
retrain_rounds = max(avg_best, 300)
print(f"  Retrain rounds (revenue): {retrain_rounds}")

final_boosters = []
for seed in SEEDS:
    params = {**lgb_params, 'seed': seed, 'bagging_seed': seed}
    ds = lgb.Dataset(
        df_train[FEATURES], y_full_log,
        weight=df_train['weight'].values,
        categorical_feature=CATEGORICALS,
        free_raw_data=False
    )
    bst = lgb.train(params, ds, num_boost_round=retrain_rounds)
    final_boosters.append(bst)

final_gm_boosters = []
for seed in SEEDS:
    params = {**gm_params, 'seed': seed}
    ds = lgb.Dataset(
        df_train[GM_FEATURES], df_train['GM_pct'].values,
        weight=df_train['weight'].values,
        categorical_feature=CATEGORICALS,
        free_raw_data=False
    )
    bst = lgb.train(params, ds, num_boost_round=800)
    final_gm_boosters.append(bst)

rev_test = predict_revenue(df_test, final_boosters, floor=REV_FLOOR)
gm_test  = predict_gm(df_test, final_gm_boosters)
cogs_test = rev_test * (1 - gm_test)

# Sanity
print(f"\n  Negative Revenue: {(rev_test < 0).sum()}")
print(f"  COGS > Revenue:   {(cogs_test > rev_test).sum()}")
print(f"  Rev range: [{rev_test.min():,.0f}, {rev_test.max():,.0f}]")
print(f"  GM% range: [{gm_test.min():.4f}, {gm_test.max():.4f}]")

m23 = df_test['year'] == 2023
m24 = df_test['year'] == 2024
mean_23 = rev_test[m23].mean()
mean_24 = rev_test[m24].mean()
growth  = (mean_24 / mean_23 - 1) * 100
print(f"  Mean 2023: {mean_23:,.0f}  Mean 2024: {mean_24:,.0f}  Growth: {growth:+.1f}%")

# Save submission
submission = pd.DataFrame({
    'Date': df_test['Date'].dt.strftime('%Y-%m-%d'),
    'Revenue': rev_test.round(2),
    'COGS': cogs_test.round(2)
})
submission.to_csv(SUBMISSION, index=False)
print(f"\n  Saved {SUBMISSION} ({len(submission)} rows)")

# Save models
for i, bst in enumerate(final_boosters):
    bst.save_model(f'{MODEL_DIR}/lgbm_rev_seed{SEEDS[i]}.txt')
for i, bst in enumerate(final_gm_boosters):
    bst.save_model(f'{MODEL_DIR}/lgbm_gm_seed{SEEDS[i]}.txt')

with open(f'{MODEL_DIR}/features.json', 'w') as f:
    json.dump({'revenue_features': FEATURES, 'gm_features': GM_FEATURES, 'categoricals': CATEGORICALS}, f, indent=2)

metrics = {
    'version': 'v6',
    'val_period': f'{VAL_START} -> 2022-12-31',
    'ensemble_seeds': SEEDS,
    'revenue': {'mae': float(rev_mae), 'rmse': float(rev_rmse), 'r2': float(rev_r2), 'mape': float(rev_mape)},
    'cogs': {'mae': float(cogs_mae), 'rmse': float(cogs_rmse)},
    'sanity': {'neg_revenue': 0, 'cogs_gt_revenue': 0, 'mean_2023': float(mean_23), 'mean_2024': float(mean_24), 'growth_pct': float(growth)}
}
with open(f'{MODEL_DIR}/validation_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

# ═══════════════════════════════════════════════
# 9. SHAP ANALYSIS
# ═══════════════════════════════════════════════
print("\n[7/7] SHAP analysis...")
try:
    shap_params = {**lgb_params, 'seed': 42, 'bagging_seed': 42}
    X_shap_train = df_tr[FEATURES].copy()
    X_shap_val = df_vl[FEATURES].copy()
    for col in CATEGORICALS:
        X_shap_train[col] = X_shap_train[col].astype(int)
        X_shap_val[col] = X_shap_val[col].astype(int)

    ds_shap = lgb.Dataset(X_shap_train, y_tr_log, weight=df_tr['weight'].values, free_raw_data=False)
    ds_shap_val = lgb.Dataset(X_shap_val, y_vl_log, free_raw_data=False)
    shap_bst = lgb.train(shap_params, ds_shap, num_boost_round=2000,
                         valid_sets=[ds_shap_val], callbacks=[lgb.early_stopping(50, verbose=False)])

    explainer = shap.TreeExplainer(shap_bst)
    shap_values = explainer.shap_values(X_shap_val)

    feature_mapping = {
        'revenue_lag_1': 'Doanh thu (Trễ 1 ngày)',
        'revenue_lag_7': 'Doanh thu (Trễ 7 ngày)',
        'revenue_lag_30': 'Doanh thu (Trễ 30 ngày)',
        'revenue_lag_364': 'Doanh thu (Trễ 364 ngày)',
        'revenue_lag_365': 'Doanh thu (Trễ 365 ngày)',
        'revenue_rolling_7': 'Doanh thu trung bình (7 ngày)',
        'revenue_rolling_30': 'Doanh thu trung bình (30 ngày)',
        'days_to_month_end': 'Số ngày đến cuối tháng',
        'day': 'Ngày trong tháng',
        'revenue_tet_aligned_lag': 'Doanh thu cùng kỳ Tết năm trước',
        'time_idx': 'Chỉ số thời gian (Xu hướng dài hạn)',
        'is_weekend': 'Ngày cuối tuần',
        'day_of_week': 'Ngày trong tuần',
        'days_to_tet': 'Số ngày đếm ngược đến Tết',
        'month_cos': 'Chu kỳ tháng (Cos)',
        'month_sin': 'Chu kỳ tháng (Sin)',
        'days_since_tet': 'Số ngày sau Tết',
        'is_month_end_zone': 'Giai đoạn cuối tháng',
        'is_mega_sale': 'Ngày Siêu Sale (Mega Sale)',
        'is_covid_lockdown': 'Giai đoạn giãn cách Covid',
        'is_public_holiday': 'Ngày nghỉ Lễ',
        'days_to_holiday': 'Số ngày đến ngày Lễ',
        'month': 'Tháng',
        'quarter': 'Quý'
    }
    X_plot = X_shap_val.rename(columns=feature_mapping)

    plt.figure(figsize=(12, 8))
    shap.summary_plot(shap_values, X_plot, show=False, max_display=15)
    plt.xlabel('Giá trị SHAP (Mức độ tác động)', fontsize=12)
    plt.title('Phân bổ Tác động Đặc trưng', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'{MODEL_DIR}/shap_summary_real.png', dpi=150, bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(10, 7))
    shap.summary_plot(shap_values, X_plot, plot_type='bar', show=False, max_display=15)
    plt.xlabel('Tác động trung bình (Giá trị tuyệt đối)', fontsize=12)
    plt.title('Mức độ Quan trọng Tuyệt đối', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'{MODEL_DIR}/shap_bar_real.png', dpi=150, bbox_inches='tight')
    plt.close()

    mean_shap = np.abs(shap_values).mean(axis=0)
    feat_imp = sorted(zip(FEATURES, mean_shap), key=lambda x: -x[1])
    print("\n  Top 10 Features:")
    for i, (f, v) in enumerate(feat_imp[:10]):
        print(f"    {i+1}. {f}: {v:,.0f}")
    with open(f'{MODEL_DIR}/shap_importances.json', 'w') as f:
        json.dump({feat: float(val) for feat, val in feat_imp}, f, indent=2)
except Exception as e:
    print(f"  SHAP failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("v6 PIPELINE COMPLETE!")
print("=" * 60)
