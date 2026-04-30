import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.ticker as ticker

# Create output folder
output_dir_nopbai = r"e:\project\datathon-2026-round-1\Nop_bai"
output_dir_path2 = r"e:\project\datathon-2026-round-1\Path2\Nop_Bai"
os.makedirs(output_dir_nopbai, exist_ok=True)
os.makedirs(output_dir_path2, exist_ok=True)

data_path = r"e:\project\datathon-2026-round-1\Analysis\merged_inventory_products.csv"
print("Reading data...")
df = pd.read_csv(data_path)

if 'product_name_x' in df.columns:
    df['product_name'] = df['product_name_x']
else:
    df['product_name'] = df['product_name']

# Calculate total profit
df['unit_profit'] = df['price'] - df['cogs']
df['total_profit'] = df['units_sold'] * df['unit_profit']

# Aggregate by product
product_perf = df.groupby(['product_id', 'product_name']).agg({
    'total_profit': 'sum',
    'overstock_flag': 'mean'
}).reset_index()

profit_cutoff = product_perf['total_profit'].quantile(0.10) 
overstock_cutoff = 0.5 

# Get bottom 10 products by profit
bottom_products = product_perf.sort_values('total_profit', ascending=True).head(10).reset_index(drop=True)

sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'

fig, ax1 = plt.subplots(figsize=(14, 8))

# Define colors based on Drop criteria
colors = ['#d62828' if (row['total_profit'] <= profit_cutoff and row['overstock_flag'] > overstock_cutoff) else '#8d99ae' for idx, row in bottom_products.iterrows()]

# 1. Bar Chart for Profit
bars = ax1.barh(bottom_products['product_name'], bottom_products['total_profit'], color=colors, alpha=0.85, edgecolor='black')

ax1.set_xlabel('Tổng Lợi Nhuận ($)', fontsize=13, fontweight='bold')
ax1.set_ylabel('Tên Sản Phẩm', fontsize=13, fontweight='bold')
ax1.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{x:,.0f} $'))

# Add profit labels on bars
for bar in bars:
    width = bar.get_width()
    ax1.annotate(f"{width:,.0f} $",
                 xy=(width, bar.get_y() + bar.get_height() / 2),
                 xytext=(5, 0),  
                 textcoords="offset points",
                 ha='left', va='center', fontsize=11, fontweight='bold')

# 2. Lollipop/Dot for Overstock Rate on secondary X-axis
ax2 = ax1.twiny()
ax2.plot(bottom_products['overstock_flag'], bottom_products['product_name'], 'o', color='#f77f00', markersize=12, markeredgecolor='black', linewidth=2, linestyle='-')
ax2.set_xlabel('Tỷ lệ Overstock (0 - 1)', fontsize=13, fontweight='bold', color='#f77f00')
ax2.set_xlim(0, max(bottom_products['overstock_flag'].max() * 1.2, 1.0))

# Add overstock labels
for i, txt in enumerate(bottom_products['overstock_flag']):
    ax2.annotate(f"{txt:.2f}",
                 xy=(txt, bottom_products['product_name'][i]),
                 xytext=(0, -12),  
                 textcoords="offset points",
                 ha='center', va='top', fontsize=10, fontweight='bold', color='#c06014')

ax1.invert_yaxis()  # Put the worst at the top

# Title
plt.title('ĐỀ XUẤT NGỪNG KINH DOANH: TOP 10 SẢN PHẨM KÉM HIỆU QUẢ NHẤT\n(Sản phẩm màu đỏ: Lợi nhuận thuộc nhóm 10% thấp nhất VÀ Tỷ lệ Overstock > 50%)', fontsize=16, fontweight='bold', pad=20)

# Custom legend
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
legend_elements = [
    Patch(facecolor='#d62828', edgecolor='black', label='Đề xuất Ngừng KD (Cắt giảm)'),
    Patch(facecolor='#8d99ae', edgecolor='black', label='Cần theo dõi thêm (Giữ lại)'),
    Line2D([0], [0], marker='o', color='#f77f00', label='Tỷ lệ Overstock', markerfacecolor='#f77f00', markersize=10, linestyle='-')
]
ax1.legend(handles=legend_elements, loc='lower right', fontsize=12, borderpad=1)

plt.tight_layout()

output_path_1 = os.path.join(output_dir_nopbai, '3_Prescriptive_Drop_Products.png')
output_path_2 = os.path.join(output_dir_path2, '3_Prescriptive_Drop_Products.png')

plt.savefig(output_path_1, dpi=300, bbox_inches='tight')
plt.savefig(output_path_2, dpi=300, bbox_inches='tight')
plt.close()

print(f"Saved chart to {output_path_1} and {output_path_2}")
