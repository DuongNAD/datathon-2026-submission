import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import matplotlib.ticker as ticker
from matplotlib.patches import Rectangle

# Setup paths
data_dir = r"e:\project\datathon-2026-round-1"
out_dir = os.path.join(data_dir, "Path2", "Nop_Bai", "Hien")
os.makedirs(out_dir, exist_ok=True)

print("Reading data...")
orders = pd.read_csv(os.path.join(data_dir, "orders.csv"))
order_items = pd.read_csv(os.path.join(data_dir, "order_items.csv"), low_memory=False)
products = pd.read_csv(os.path.join(data_dir, "products.csv"))

# Filter orders: Exclude cancelled and returned
orders_filtered = orders[~orders['order_status'].isin(['cancelled', 'returned'])].copy()

# Merge
df = pd.merge(order_items, orders_filtered, on='order_id', how='inner')
df = pd.merge(df, products[['product_id', 'cogs']], on='product_id', how='left')

# Convert order_date to datetime
df['order_date'] = pd.to_datetime(df['order_date'])

# Calculations
# Treat discount_amount as an absolute deduction from the total item price line
df['revenue'] = (df['quantity'] * df['unit_price']) - df['discount_amount'].fillna(0)
df['total_cogs'] = df['quantity'] * df['cogs']

# Extract Year and Month
df['year'] = df['order_date'].dt.year
df['month'] = df['order_date'].dt.month
df['year_month'] = df['order_date'].dt.to_period('M')

# Grouping at the monthly level
monthly_data = df.groupby(['year', 'month', 'year_month']).agg(
    total_rev=('revenue', 'sum'),
    total_cogs=('total_cogs', 'sum')
).reset_index()

monthly_data['gross_margin'] = monthly_data['total_rev'] - monthly_data['total_cogs']
monthly_data['gross_margin_pct'] = (monthly_data['gross_margin'] / monthly_data['total_rev']) * 100

# Sort by time
monthly_data = monthly_data.sort_values(['year', 'month']).reset_index(drop=True)
monthly_data['time_index'] = range(len(monthly_data))
monthly_data['year_month_str'] = monthly_data['year'].astype(str) + "-" + monthly_data['month'].astype(str).str.zfill(2)

# Export data to CSV
csv_path = os.path.join(out_dir, "6_Gross_Margin_Data.csv")
monthly_data.to_csv(csv_path, index=False)
print(f"Data successfully saved to: {csv_path}")

# ==========================================
# VISUALIZATION SETUP
# ==========================================
sns.set_theme(style="whitegrid")
# ------------------------------------------
# CHART 1: GROSS MARGIN TREND (OVERALL)
# ------------------------------------------
fig1, ax1 = plt.subplots(figsize=(14, 8))
ax1.plot(monthly_data['time_index'], monthly_data['gross_margin_pct'], color='steelblue', linewidth=2, zorder=2)

# Safe Zone background (10% to 20%)
ax1.axhspan(10, 20, facecolor='lightgreen', alpha=0.3, zorder=1, label='Vùng Lợi Nhuận An Toàn (10-20%)')

# Highlights
odd_aug_mask = (monthly_data['month'] == 8) & (monthly_data['year'] % 2 != 0)
dec_mask = (monthly_data['month'] == 12) & (monthly_data['year'].isin([2013, 2014]))

ax1.scatter(monthly_data.loc[odd_aug_mask, 'time_index'], monthly_data.loc[odd_aug_mask, 'gross_margin_pct'], 
            color='darkred', s=150, zorder=4, edgecolor='white', linewidth=2, label='Thủng Đáy (T8 - Năm lẻ)')

ax1.scatter(monthly_data.loc[dec_mask, 'time_index'], monthly_data.loc[dec_mask, 'gross_margin_pct'], 
            color='orange', s=150, zorder=4, edgecolor='white', linewidth=2, label='Lỗ Nặng Thực Tế T12 (Sau khi lọc data)')

# Annotations for chart 1
for _, row in monthly_data[odd_aug_mask].iterrows():
    ax1.annotate(f"{row['gross_margin_pct']:.1f}%",
                 xy=(row['time_index'], row['gross_margin_pct']),
                 xytext=(0, -25), textcoords='offset points', ha='center', color='darkred', fontweight='bold')

for _, row in monthly_data[dec_mask].iterrows():
    ax1.annotate(f"{row['gross_margin_pct']:.1f}%",
                 xy=(row['time_index'], row['gross_margin_pct']),
                 xytext=(0, 15), textcoords='offset points', ha='center', color='darkorange', fontweight='bold')

ax1.set_title("XU HƯỚNG BIÊN LỢI NHUẬN GỘP (GROSS MARGIN TREND)", fontsize=16, fontweight='bold', pad=15)
ax1.set_ylabel("Biên Lợi Nhuận Gộp (%)", fontsize=12)
ax1.set_xlabel("Thời gian (Năm-Tháng)", fontsize=12)

# Set X ticks
tick_idx = np.arange(0, len(monthly_data), 6)  # Tick every 6 months for better visibility
ax1.set_xticks(tick_idx)
ax1.set_xticklabels(monthly_data['year_month_str'].iloc[tick_idx], rotation=45, ha='right')

ax1.legend(loc='upper right', fontsize=11)
ax1.set_ylim(-45, 30)

plt.tight_layout()
chart1_path = os.path.join(out_dir, "6a_Gross_Margin_Trend.png")
plt.savefig(chart1_path, dpi=300, bbox_inches='tight')
print(f"Chart 1 successfully saved to: {chart1_path}")
plt.close(fig1)

# ------------------------------------------
# CHART 2: SEASONALITY PLOT
# ------------------------------------------
fig2, ax2 = plt.subplots(figsize=(10, 8))
years = monthly_data['year'].unique()
for year in years:
    year_data = monthly_data[monthly_data['year'] == year]
    
    if year % 2 != 0:
        # Odd years: Bold Red
        ax2.plot(year_data['month'], year_data['gross_margin_pct'], color='crimson', linewidth=2.5, alpha=0.8)
    else:
        # Even years: Darker Gray
        ax2.plot(year_data['month'], year_data['gross_margin_pct'], color='darkgray', linewidth=1.5, alpha=0.7)

ax2.set_title("CHU KỲ MÙA VỤ THEO TỪNG NĂM", fontsize=16, fontweight='bold', pad=15)
ax2.set_xlabel("Tháng", fontsize=12)
ax2.set_ylabel("Biên Lợi Nhuận Gộp (%)", fontsize=12)
ax2.set_xticks(range(1, 13))
ax2.set_xticklabels([f"T{i}" for i in range(1, 13)])
ax2.set_ylim(-45, 30)

# Custom legend for seasonality
from matplotlib.lines import Line2D
custom_lines = [Line2D([0], [0], color='crimson', lw=2.5),
                Line2D([0], [0], color='darkgray', lw=1.5)]
ax2.legend(custom_lines, ['Năm Lẻ (2013, 15, 17, 19, 21)', 'Năm Chẵn'], loc='lower left', fontsize=11)

# Annotate the extreme dip area
ax2.add_patch(Rectangle((7.5, -45), 1, 15, facecolor='red', alpha=0.1, zorder=0))
ax2.text(8, -35, 'Thủng đáy\nT8', color='darkred', ha='center', va='center', fontweight='bold', alpha=0.6)

plt.tight_layout()

# Save
chart2_path = os.path.join(out_dir, "6b_Gross_Margin_Seasonality.png")
plt.savefig(chart2_path, dpi=300, bbox_inches='tight')
print(f"Chart 2 successfully saved to: {chart2_path}")
plt.close(fig2)
