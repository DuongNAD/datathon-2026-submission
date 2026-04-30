import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# Create output folder
output_dir_nopbai = r"e:\project\datathon-2026-round-1\Nop_bai"
output_dir_path2 = r"e:\project\datathon-2026-round-1\Path2\Nop_Bai"
os.makedirs(output_dir_nopbai, exist_ok=True)
os.makedirs(output_dir_path2, exist_ok=True)

# Read merged data
data_path = r"e:\project\datathon-2026-round-1\Analysis\merged_inventory_products.csv"
print("Reading data...")
df = pd.read_csv(data_path)

if 'category_x' in df.columns:
    df['category'] = df['category_x']
elif 'category_y' in df.columns:
    df['category'] = df['category_y']

risk_df = df.groupby('category').agg({
    'overstock_flag': 'mean',
    'stockout_days': 'mean',
    'sell_through_rate': 'mean'
}).reset_index()

risk_df = risk_df.sort_values(by='overstock_flag', ascending=False).reset_index(drop=True)

# Set up the figure
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'

fig, ax1 = plt.subplots(figsize=(14, 8))

x = np.arange(len(risk_df['category']))
width = 0.35

# Plot Bars for Rates on Primary Y-axis
bar1 = ax1.bar(x - width/2, risk_df['overstock_flag'], width, label='Tỷ lệ Overstock', color='#ff9999', edgecolor='black', alpha=0.85)
bar2 = ax1.bar(x + width/2, risk_df['sell_through_rate'], width, label='Tỷ lệ Bán ra', color='#457b9d', edgecolor='black', alpha=0.85)

ax1.set_ylabel('Tỷ Lệ (0 - 1)', fontsize=13, fontweight='bold')
ax1.set_xlabel('Danh Mục Sản Phẩm', fontsize=13, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(risk_df['category'], fontsize=12)
ax1.set_ylim(0, max(risk_df['overstock_flag'].max(), risk_df['sell_through_rate'].max()) * 1.3)

# Data labels for bars
for p in ax1.patches:
    height = p.get_height()
    ax1.annotate(f"{height:.3f}", (p.get_x() + p.get_width() / 2., height), 
                 ha='center', va='bottom', fontsize=11, xytext=(0, 4), textcoords='offset points', fontweight='bold')

# Plot Line for Stockout Days on Secondary Y-axis
ax2 = ax1.twinx()
line1 = ax2.plot(x - width/2, risk_df['stockout_days'], label='Số ngày Hết hàng', color='#f4a261', marker='o', markersize=10, linewidth=3, markeredgecolor='black')

ax2.set_ylabel('Số ngày Hết hàng', fontsize=13, fontweight='bold', color='#d68c45')
ax2.set_ylim(0, risk_df['stockout_days'].max() * 1.6)
ax2.grid(False) # Turn off grid for secondary axis to avoid clutter

# Data labels for line
for i, txt in enumerate(risk_df['stockout_days']):
    ax2.annotate(f"{txt:.3f} ngày", (x[i] - width/2, risk_df['stockout_days'][i]), 
                 ha='center', va='bottom', fontsize=11, xytext=(0, 10), textcoords='offset points', fontweight='bold', color='#c06014')

# Title & Legend
plt.title('PHÂN TÍCH RỦI RO TỒN KHO THEO DANH MỤC', fontsize=18, fontweight='bold', pad=20)

# Combine legends
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper center', bbox_to_anchor=(0.5, 0.98), ncol=3, fontsize=12, framealpha=0.9)

plt.tight_layout()

output_path_1 = os.path.join(output_dir_nopbai, '2_Inventory_Risk_Analysis.png')
output_path_2 = os.path.join(output_dir_path2, '2_Inventory_Risk_Analysis_Redesigned.png')

plt.savefig(output_path_1, dpi=300, bbox_inches='tight')
plt.savefig(output_path_2, dpi=300, bbox_inches='tight')
plt.close()

print(f"Saved chart to {output_path_1} and {output_path_2}")
