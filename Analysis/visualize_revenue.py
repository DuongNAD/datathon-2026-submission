import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

# Setup paths
data_dir = r"e:\project\datathon-2026-round-1"
out_dir = os.path.join(data_dir, "Path2")
nop_bai_dir = os.path.join(data_dir, "Nop_bai")

os.makedirs(out_dir, exist_ok=True)
os.makedirs(nop_bai_dir, exist_ok=True)

print("Reading data...")
orders = pd.read_csv(os.path.join(data_dir, "orders.csv"))
order_items = pd.read_csv(os.path.join(data_dir, "order_items.csv"), low_memory=False)

# Merge
df = pd.merge(order_items, orders, on='order_id', how='left')

# Calculate Revenue (Gross Sales)
df['revenue'] = df['quantity'] * df['unit_price']
df['order_date'] = pd.to_datetime(df['order_date'])

# Extract Year and Month
df['year'] = df['order_date'].dt.year
df['month'] = df['order_date'].dt.month

# 1. Yearly Revenue
yearly_revenue = df.groupby('year')['revenue'].sum().reset_index()
yearly_revenue_csv_path = os.path.join(out_dir, "revenue_by_year.csv")
yearly_revenue.to_csv(yearly_revenue_csv_path, index=False)
print(f"Exported {yearly_revenue_csv_path}")

# 2. Monthly Revenue (Total across all years to find the best months)
monthly_revenue = df.groupby('month')['revenue'].sum().reset_index()
monthly_revenue_csv_path = os.path.join(out_dir, "revenue_by_month.csv")
monthly_revenue.to_csv(monthly_revenue_csv_path, index=False)
print(f"Exported {monthly_revenue_csv_path}")

# ==========================================
# VISUALIZATION 1: YEARLY TREND
# ==========================================
sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))

sns.lineplot(data=yearly_revenue, x='year', y='revenue', marker='o', linewidth=3, color='royalblue')

# Annotate peak (2016)
peak_row = yearly_revenue.loc[yearly_revenue['revenue'].idxmax()]
plt.annotate(f"Đỉnh 2016\n(~2.1 Tỷ VNĐ)",
             xy=(peak_row['year'], peak_row['revenue']),
             xytext=(peak_row['year'], peak_row['revenue'] + 0.15e9),
             ha='center',
             arrowprops=dict(facecolor='red', shrink=0.05, width=2, headwidth=8),
             fontsize=12, fontweight='bold', color='darkred')

# Format axes
plt.ylim(0.6e9, 2.5e9)
plt.title("XU HƯỚNG TĂNG TRƯỞNG DOANH THU THEO NĂM", fontsize=14, fontweight='bold', pad=40)
plt.xlabel("Năm", fontsize=12)
plt.ylabel("Doanh Thu (VNĐ)", fontsize=12)

# Add Legend
legend_elements_1 = [Line2D([0], [0], color='royalblue', lw=3, marker='o', label='Doanh thu tổng (VNĐ)')]
plt.legend(handles=legend_elements_1, loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=1, frameon=False, fontsize=12)
plt.xticks(yearly_revenue['year'])
plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x*1e-9:.1f} Tỷ"))

plt.tight_layout()
chart1_path = os.path.join(nop_bai_dir, "4a_Revenue_Yearly.png")
plt.savefig(chart1_path, dpi=300, bbox_inches='tight')
print(f"Chart 1 saved to {chart1_path}")
plt.close()

# ==========================================
# VISUALIZATION 2: MONTHLY SEASONALITY
# ==========================================
plt.figure(figsize=(10, 6))

# Highlight months 4, 5, and 6
colors = ['lightgray' if m not in [4, 5, 6] else 'coral' for m in monthly_revenue['month']]
sns.barplot(data=monthly_revenue, x='month', y='revenue', hue='month', palette=colors, legend=False)

# Format axes
plt.title("CÁC THÁNG CAO ĐIỂM: DOANH THU THEO TỪNG THÁNG", fontsize=14, fontweight='bold', pad=40)
plt.xlabel("Tháng", fontsize=12)
plt.ylabel("Tổng Doanh Thu (VNĐ)", fontsize=12)
plt.xticks(range(0, 12), [f"T{i}" for i in range(1, 13)])
plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x*1e-9:.1f} Tỷ"))

# Add custom legend for highlight
red_patch = mpatches.Patch(color='coral', label='Các tháng cao điểm (Tháng 4, 5 & 6)')
gray_patch = mpatches.Patch(color='lightgray', label='Các tháng khác')
plt.legend(handles=[red_patch, gray_patch], loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=2, frameon=False, fontsize=12)

plt.tight_layout()
chart2_path = os.path.join(nop_bai_dir, "4b_Revenue_Monthly.png")
plt.savefig(chart2_path, dpi=300, bbox_inches='tight')
print(f"Chart 2 saved to {chart2_path}")
plt.close()

