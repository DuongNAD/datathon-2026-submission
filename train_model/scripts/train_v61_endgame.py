"""V61 ENDGAME - Time-varying multiplier to hedge Public/Private LB shake-up"""
import pandas as pd, numpy as np, os

SD = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SD, '..', '..'))
DD = os.path.join(SD, '..', 'dataset')
OUT_V55 = os.path.join(SD, 'model_v55')

print("="*70)
print("V61 ENDGAME - TIME-VARYING MULTIPLIER HEDGE")
print("="*70)

# Load V55 best predictions
ml_pred = np.load(f'{OUT_V55}/ml_pred.npy')
cr = np.load(f'{OUT_V55}/cr_pred.npy')
naive_pred = np.load(f'{OUT_V55}/naive_pred.npy')
naive_cogs = np.load(f'{OUT_V55}/naive_cogs.npy')

df_test = pd.read_csv(f'{DD}/sales_test.csv', parse_dates=['Date'])
dates = df_test['Date'].dt.strftime('%Y-%m-%d').values
test_dates = df_test['Date'].values
sub_dir = os.path.join(ROOT, 'Nop_bai')
bml = 0.90
blend = bml * ml_pred + (1-bml) * naive_pred

# Analyze test set structure
n_2023 = (df_test['Date'].dt.year == 2023).sum()
n_2024 = (df_test['Date'].dt.year == 2024).sum()
print(f"  Test: {n_2023} days in 2023 + {n_2024} days in 2024 = {len(df_test)} total")

# Historical YoY growth pattern:
# 2021->2022: +12.1%
# If 2022->2023 continues at ~12-15%, and 2023->2024 slows to ~5-8%
# Then multiplier should DECAY over time

# === STRATEGY: Time-varying multiplier ===
# The multiplier compensates for model under-prediction.
# Model trained on 2012-2022 predicts ~2022 level.
# 2023 needs higher mult (strong recovery), 2024 needs lower (momentum fades)

def time_varying_mult(dates, m_start, m_end):
    """Linear interpolation from m_start (2023-01-01) to m_end (2024-07-01)"""
    t0 = pd.Timestamp('2023-01-01')
    t1 = pd.Timestamp('2024-07-01')
    t = pd.to_datetime(dates)
    frac = np.clip((t - t0) / (t1 - t0), 0, 1)
    return m_start + (m_end - m_start) * frac

def step_mult(dates, m_2023, m_2024):
    """Step function: different multiplier per year"""
    t = pd.to_datetime(dates)
    mult = np.where(t.year == 2023, m_2023, m_2024)
    return mult

def save_sub(frev, name):
    fcogs = np.clip(frev * cr, 0, frev)  # simplified COGS
    pd.DataFrame({'Date': dates, 'Revenue': frev.round(2), 'COGS': fcogs.round(2)}).to_csv(
        os.path.join(sub_dir, f'submission_{name}.csv'), index=False)
    r23 = frev[df_test['Date'].dt.year.values == 2023].mean()
    r24 = frev[df_test['Date'].dt.year.values == 2024].mean()
    print(f"  {name:35s} | 2023={r23:>10,.0f} | 2024={r24:>10,.0f} | All={frev.mean():>10,.0f}")

print("\n--- Reference: V55 Global m=1.28 ---")
save_sub(blend * 1.28, 'v55_global_128')

# === A: Linear Decay ===
print("\n--- A: Linear Decay Multiplier ---")
configs_linear = [
    (1.30, 1.20, 'v61_linear_130_120'),
    (1.30, 1.25, 'v61_linear_130_125'),
    (1.32, 1.20, 'v61_linear_132_120'),
    (1.28, 1.20, 'v61_linear_128_120'),
    (1.28, 1.25, 'v61_linear_128_125'),
    (1.30, 1.22, 'v61_linear_130_122'),
    (1.35, 1.15, 'v61_linear_135_115'),
    (1.32, 1.22, 'v61_linear_132_122'),
]
for m_s, m_e, name in configs_linear:
    mult = time_varying_mult(test_dates, m_s, m_e)
    save_sub(blend * mult, name)

# === B: Step Function (Year-based) ===
print("\n--- B: Step Function (2023 vs 2024) ---")
configs_step = [
    (1.28, 1.20, 'v61_step_128_120'),
    (1.28, 1.25, 'v61_step_128_125'),
    (1.30, 1.20, 'v61_step_130_120'),
    (1.30, 1.25, 'v61_step_130_125'),
    (1.32, 1.20, 'v61_step_132_120'),
    (1.32, 1.22, 'v61_step_132_122'),
    (1.35, 1.15, 'v61_step_135_115'),
]
for m23, m24, name in configs_step:
    mult = step_mult(test_dates, m23, m24)
    save_sub(blend * mult, name)

# === C: Quarterly Multiplier ===
print("\n--- C: Quarterly Multiplier ---")
def quarterly_mult(dates, q_mults):
    t = pd.to_datetime(dates)
    yr = t.year
    qt = t.quarter
    mult = np.ones(len(dates))
    for (y, q), m in q_mults.items():
        mult[(yr == y) & (qt == q)] = m
    return mult

q_configs = [
    ('v61_quarterly_v1', {
        (2023,1): 1.30, (2023,2): 1.30, (2023,3): 1.28, (2023,4): 1.28,
        (2024,1): 1.22, (2024,2): 1.22, (2024,3): 1.20
    }),
    ('v61_quarterly_v2', {
        (2023,1): 1.32, (2023,2): 1.30, (2023,3): 1.28, (2023,4): 1.26,
        (2024,1): 1.22, (2024,2): 1.20, (2024,3): 1.18
    }),
    ('v61_quarterly_v3', {
        (2023,1): 1.28, (2023,2): 1.28, (2023,3): 1.28, (2023,4): 1.28,
        (2024,1): 1.25, (2024,2): 1.22, (2024,3): 1.20
    }),
]
for name, qm in q_configs:
    mult = quarterly_mult(test_dates, qm)
    save_sub(blend * mult, name)

# === Summary ===
print("\n" + "="*70)
print("HEDGE STRATEGY:")
print("  Submission 1 (Public LB): V55 m=1.28 global (740K proven)")
print("  Submission 2 (Hedge):     V61 time-varying (protects vs Private LB)")
print("="*70)
