"""Check submission v6 against all competition constraints."""
import pandas as pd
import numpy as np

sub = pd.read_csv('submission_v6.csv', parse_dates=['Date'])
sample = pd.read_csv('../sample_submission.csv', parse_dates=['Date'])

print("=" * 60)
print("KIEM TRA RANG BUOC — SUBMISSION v6")
print("=" * 60)

checks = {}

# 1. Format
cols_ok = list(sub.columns) == ["Date", "Revenue", "COGS"]
checks["Format (Date,Revenue,COGS)"] = cols_ok
print(f"\n[1] Columns: {list(sub.columns)} -> {'PASS' if cols_ok else 'FAIL'}")

# 2. Row count
rows_ok = len(sub) == len(sample)
checks["Row count matches"] = rows_ok
print(f"[2] Rows: {len(sub)} vs {len(sample)} -> {'PASS' if rows_ok else 'FAIL'}")

# 3. Date range
dr_ok = sub['Date'].min().date() == sample['Date'].min().date() and sub['Date'].max().date() == sample['Date'].max().date()
checks["Date range"] = dr_ok
print(f"[3] Date range: {sub['Date'].min().date()} -> {sub['Date'].max().date()} -> {'PASS' if dr_ok else 'FAIL'}")

# 4. Date order
if len(sub) == len(sample):
    dates_ok = (sub['Date'] == sample['Date']).all()
    checks["Date order matches"] = dates_ok
    print(f"[4] Date order match: {'PASS' if dates_ok else 'FAIL'}")

# 5. No negatives
neg_rev = (sub['Revenue'] < 0).sum()
neg_cogs = (sub['COGS'] < 0).sum()
checks["No negative Revenue"] = neg_rev == 0
checks["No negative COGS"] = neg_cogs == 0
print(f"[5] Negative Rev: {neg_rev}, Negative COGS: {neg_cogs}")

# 6. COGS < Revenue
violations = (sub['COGS'] > sub['Revenue']).sum()
checks["COGS <= Revenue"] = violations == 0
print(f"[6] COGS > Revenue: {violations}")

# 7. No NaN
nan_count = sub.isna().sum().sum()
checks["No NaN"] = nan_count == 0
print(f"[7] NaN values: {nan_count}")

# 8. Stats
gm = (sub['Revenue'] - sub['COGS']) / sub['Revenue']
print(f"\n[Stats]")
print(f"  Revenue: min={sub['Revenue'].min():,.0f} max={sub['Revenue'].max():,.0f} mean={sub['Revenue'].mean():,.0f}")
print(f"  COGS:    min={sub['COGS'].min():,.0f} max={sub['COGS'].max():,.0f} mean={sub['COGS'].mean():,.0f}")
print(f"  GM%:     min={gm.min():.4f} max={gm.max():.4f} mean={gm.mean():.4f}")

print(f"\n{'=' * 60}")
print("SUMMARY")
for name, passed in checks.items():
    print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
print(f"\n  Overall: {'ALL PASSED' if all(checks.values()) else 'SOME FAILED'}")
