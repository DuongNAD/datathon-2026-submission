"""
evaluate.py — Script đánh giá mô hình v3 FINAL
Load model artifacts từ model/ và chạy backtesting + sanity check.
"""
import pandas as pd
import numpy as np
import holidays
import lightgbm as lgb
import joblib
import json
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

MODEL_DIR  = 'model'
DATA_DIR   = 'dataset'

# ── Load Model Artifacts ──
print("Loading model artifacts...")
trend_model  = joblib.load(f'{MODEL_DIR}/trend_linear_regression.pkl')
lgbm_booster = lgb.Booster(model_file=f'{MODEL_DIR}/lgbm_residuals.txt')
margin_ratio = float(np.load(f'{MODEL_DIR}/margin_ratio.npy'))
with open(f'{MODEL_DIR}/features.json', 'r') as f:
    feat_dict = json.load(f)
features = feat_dict['features']
categorical_features = feat_dict['categorical']
with open(f'{MODEL_DIR}/validation_metrics.json', 'r') as f:
    metrics = json.load(f)

print(f"Model version: {metrics.get('version', 'unknown')}")
print(f"Features: {features}")
print(f"Margin ratio (base): {margin_ratio:.4f}")

# ── Feature Engineering ──
def add_time_features(df):
    df = df.copy()
    df['year']  = df['Date'].dt.year
    df['month'] = df['Date'].dt.month
    df['day']   = df['Date'].dt.day
    df['day_of_week'] = df['Date'].dt.dayofweek
    df['quarter'] = df['Date'].dt.quarter
    df['is_weekend']     = df['day_of_week'].isin([5, 6]).astype(int)
    df['is_month_start'] = df['Date'].dt.is_month_start.astype(int)
    df['is_month_end']   = df['Date'].dt.is_month_end.astype(int)
    base_date = pd.to_datetime('2012-07-04')
    df['time_idx'] = (df['Date'] - base_date).dt.days

    def is_mega_sale(d):
        m, day = d.month, d.day
        if (m==2 and day==14) or (m==3 and day==8) or (m==4 and day==30) or \
           (m==5 and day==1) or (m==9 and day==2) or (m==10 and day==20) or \
           (m==9 and day==9) or (m==10 and day==10) or (m==11 and day==11) or \
           (m==12 and day==12) or (m==11 and day>=20 and day<=30 and d.dayofweek==4):
            return 1
        return 0
    df['is_mega_sale'] = df['Date'].apply(is_mega_sale)

    vn_holidays = holidays.VN(years=range(2012, 2026))
    tet_keywords = ['Tết Nguyên Đán', 'Giao thừa', '29 Tết', 'Mùng']
    tet_dates = sorted([
        date for date, name in vn_holidays.items()
        if any(kw in name for kw in tet_keywords)
    ])
    df['is_tet'] = df['Date'].dt.date.apply(lambda d: 1 if d in tet_dates else 0)
    def days_to_next_tet(d):
        future_tets = [td for td in tet_dates if td >= d.date()]
        return (future_tets[0] - d.date()).days if future_tets else 365
    df['days_to_tet'] = df['Date'].apply(days_to_next_tet)
    df['is_approaching_tet'] = (df['days_to_tet'] <= 21).astype(int)

    for col in categorical_features:
        df[col] = df[col].astype('category')
    return df

# ── Evaluate on Train (2019-2022 backtesting) ──
print("\nLoading train data...")
df_train = add_time_features(pd.read_csv(f'{DATA_DIR}/sales_train.csv', parse_dates=['Date']))
df_train = df_train[df_train['year'] >= 2019].reset_index(drop=True)

for y in [2019, 2020, 2021, 2022]:
    mask = df_train['year'] == y
    if mask.sum() == 0: continue
    X = df_train.loc[mask, features]
    t = df_train.loc[mask, ['time_idx']]
    actual = df_train.loc[mask, 'Revenue']
    pred = np.maximum(0, trend_model.predict(t) + lgbm_booster.predict(X))
    r2 = r2_score(actual, pred)
    mae = mean_absolute_error(actual, pred)
    mape = np.mean(np.abs((actual.values - pred) / actual.values)) * 100
    print(f"  {y}: R2={r2:.4f} | MAE={mae:,.0f} | MAPE={mape:.1f}%")

# ── Sanity Check on Test ──
print("\nLoading test data...")
df_test = add_time_features(pd.read_csv(f'{DATA_DIR}/sales_test.csv', parse_dates=['Date']))
X_test = df_test[features]
t_test = df_test[['time_idx']]
pred = np.maximum(0, trend_model.predict(t_test) + lgbm_booster.predict(X_test))

print(f"  Negative predictions: {(pred < 0).sum()}")
print(f"  Min: {pred.min():,.0f} | Max: {pred.max():,.0f} | Mean: {pred.mean():,.0f}")

m23 = df_test['year'] == 2023
m24 = df_test['year'] == 2024
print(f"  Mean 2023: {pred[m23].mean():,.0f}")
print(f"  Mean 2024: {pred[m24].mean():,.0f}")
print(f"  Growth: {((pred[m24].mean() / pred[m23].mean()) - 1) * 100:.1f}%")

print("\nEvaluation complete!")
