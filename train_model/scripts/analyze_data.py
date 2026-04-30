"""Quick analysis of training data for model improvement."""
import pandas as pd
import numpy as np

df = pd.read_csv('dataset/sales_train.csv', parse_dates=['Date'])
print(f"Train shape: {df.shape}")
print(f"Date range: {df.Date.min()} to {df.Date.max()}")
print(f"Years: {sorted(df.Date.dt.year.unique())}")

print("\nRevenue stats:")
print(df['Revenue'].describe())

gm = (df.Revenue - df.COGS) / df.Revenue
print("\nGM% stats:")
print(gm.describe())

print("\nBy Year:")
for y in sorted(df.Date.dt.year.unique()):
    m = df.Date.dt.year == y
    cnt = m.sum()
    rev_mean = df.loc[m, 'Revenue'].mean()
    gm_y = ((df.loc[m, 'Revenue'] - df.loc[m, 'COGS']) / df.loc[m, 'Revenue']).mean()
    print(f"  {y}: {cnt} days, Rev mean={rev_mean:,.0f}, GM%={gm_y:.4f}")

# Check month-end spike pattern
print("\nMonth-end spike analysis (day 28-31 vs day 1-27):")
df['day'] = df.Date.dt.day
df['is_month_end_zone'] = df['day'] >= 28
for label, grp in df.groupby('is_month_end_zone'):
    print(f"  Day>=28={label}: Rev mean={grp['Revenue'].mean():,.0f}, count={len(grp)}")

# Check weekly pattern
print("\nDay-of-week pattern:")
df['dow'] = df.Date.dt.dayofweek
for d in range(7):
    m = df.dow == d
    print(f"  {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][d]}: Rev mean={df.loc[m,'Revenue'].mean():,.0f}")

# Check autocorrelation at key lags
print("\nLag correlation (Revenue):")
for lag in [1, 7, 28, 30, 364, 365]:
    corr = df['Revenue'].corr(df['Revenue'].shift(lag))
    print(f"  Lag-{lag}: {corr:.4f}")

# Monthly seasonality
print("\nMonthly seasonality:")
df['month'] = df.Date.dt.month
for m in range(1, 13):
    mask = df.month == m
    print(f"  Month {m:2d}: Rev mean={df.loc[mask,'Revenue'].mean():,.0f}, GM%={gm[mask].mean():.4f}")
