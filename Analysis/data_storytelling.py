import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.ticker as ticker
from matplotlib.patches import Patch

# Create output folder
output_dir = r"e:\project\datathon-2026-round-1\Nop_bai\Images"
output_dir_path2 = r"e:\project\datathon-2026-round-1\Path2\Nop_Bai"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(output_dir_path2, exist_ok=True)

# ---------------------------------------------------------
# DATA PREPARATION
# ---------------------------------------------------------
data_path = r"e:\project\datathon-2026-round-1\Analysis\merged_inventory_products.csv"
print("Reading data...")
df = pd.read_csv(data_path)

if 'product_name_x' in df.columns:
    df['product_name'] = df['product_name_x']
else:
    df['product_name'] = df['product_name']

df['unit_profit'] = df['price'] - df['cogs']
df['total_profit'] = df['units_sold'] * df['unit_profit']

product_perf = df.groupby(['product_id', 'product_name', 'category_x']).agg({
    'total_profit': 'sum',
    'overstock_flag': 'mean'
}).reset_index()

# ==========================================
# FIX BUSINESS LOGIC: Tôn trọng tuyệt đối Luật Kinh Doanh
profit_cutoff = product_perf['total_profit'].quantile(0.10) 
drop_condition = (product_perf['total_profit'] <= profit_cutoff) & (product_perf['overstock_flag'] > 0.5)

# Danh sách ĐÚNG N sản phẩm
target_products = product_perf[drop_condition].sort_values('total_profit', ascending=True).reset_index(drop=True)
N = len(target_products)
worst_product_ids = target_products['product_id'].tolist()

# Highlight exactly these N products
product_perf['is_danger'] = product_perf['product_id'].isin(worst_product_ids)
product_perf['color'] = np.where(product_perf['is_danger'], '#e63946', '#a8dadc')
product_perf['alpha'] = np.where(product_perf['is_danger'], 1.0, 0.6)
product_perf['size'] = np.where(product_perf['is_danger'], 150, 60)

sns.set_theme(style="white")
plt.rcParams['font.family'] = 'sans-serif'

# ---------------------------------------------------------
# CHART 1: BỨC TRANH TOÀN CẢNH (Quadrant Scatter Plot)
# ---------------------------------------------------------
fig, ax1 = plt.subplots(figsize=(12, 8))

# Scatter points
for danger_status in [False, True]:
    subset = product_perf[product_perf['is_danger'] == danger_status]
    label = 'Cần Ngừng Kinh Doanh (Đọng vốn)' if danger_status else 'Bình thường'
    ax1.scatter(
        subset['overstock_flag'], 
        subset['total_profit'], 
        c=subset['color'], 
        alpha=subset['alpha'].iloc[0] if len(subset)>0 else 1, 
        s=subset['size'].iloc[0] if len(subset)>0 else 60,
        edgecolor='white' if danger_status else 'none',
        linewidth=1.5 if danger_status else 0,
        zorder=5 if danger_status else 2,
        label=label
    )

# Threshold lines
ax1.axvline(x=0.5, color='#2b2d42', linestyle='--', linewidth=1.5, zorder=1, alpha=0.6, label='Ngưỡng Tồn Kho (>50%)')
ax1.axhline(y=profit_cutoff, color='#2b2d42', linestyle='--', linewidth=1.5, zorder=1, alpha=0.6, label='Ngưỡng Lợi Nhuận (10% thấp nhất)')

# Thêm Legend
ax1.legend(loc='upper right', fontsize=11, framealpha=0.9)

# Formatting Chart 1
ax1.set_title('Ma trận Đánh giá Hiệu suất Sản phẩm', fontsize=18, fontweight='bold', pad=20, loc='center', color='#1d3557')
ax1.set_xlabel('Tỷ lệ Tồn kho vượt mức', fontsize=12, fontweight='bold', color='#457b9d')
ax1.set_ylabel('Tổng Lợi Nhuận (VNĐ)', fontsize=12, fontweight='bold', color='#457b9d')
ax1.set_yscale('log')
ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{x:,.0f}'.replace(',', '.') + ' ₫'))
ax1.set_xlim(-0.05, 1.05)

# Bỏ giới hạn trục Y để hiển thị toàn bộ dữ liệu chính xác
# ax1.set_ylim(-100000, 5000000)

# Decluttering
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_color('#cccccc')
ax1.spines['bottom'].set_color('#cccccc')
ax1.grid(False)

plt.tight_layout()
p1 = os.path.join(output_dir, 'Story_1_Quadrant_Scatter.png')
plt.savefig(p1, dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(output_dir_path2, 'Story_1_Quadrant_Scatter.png'), dpi=300, bbox_inches='tight')
plt.close()

# ---------------------------------------------------------
# CHART 2: CHỈ ĐỊNH HÀNH ĐỘNG CỤ THỂ (Horizontal Bar Chart)
# ---------------------------------------------------------
# Use exactly the N target products
bottom_10 = target_products.copy()

fig, ax2 = plt.subplots(figsize=(12, min(7, 2 + N * 0.8))) # Adjust height based on N

# Bar Chart
bars = ax2.barh(bottom_10['product_name'], bottom_10['total_profit'], color='#e63946', alpha=0.85, height=0.5)

# Formatting Chart 2
ax2.set_title(f'Chi tiết {N} sản phẩm cần xử lý ngay lập tức', fontsize=18, fontweight='bold', pad=40, loc='center', color='#1d3557')

# Thêm Legend
legend_elements_2 = [Patch(facecolor='#e63946', alpha=0.85, label='Tổng lợi nhuận sản phẩm (VNĐ)')]
ax2.legend(handles=legend_elements_2, loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=1, frameon=False, fontsize=12)

# Add Data Labels at the end of the bars
max_profit = bottom_10['total_profit'].max()
for bar, overstock in zip(bars, bottom_10['overstock_flag']):
    width = bar.get_width()
    label_text = f" Lợi nhuận: {width:,.0f}".replace(',', '.') + f" ₫  |  Tồn kho: {overstock*100:.0f}%"
    ax2.text(width + (max_profit * 0.02), bar.get_y() + bar.get_height()/2, label_text, 
             va='center', ha='left', fontsize=11, color='#2b2d42', fontweight='bold')
ax2.set_xlim(0, max_profit * 1.5)

# Decluttering
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['bottom'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax2.xaxis.set_visible(False) # Remove X-axis completely
ax2.grid(False)

# Clean Y-axis labels
ax2.tick_params(axis='y', length=0, labelsize=12)
ax2.invert_yaxis()

plt.tight_layout()
p2 = os.path.join(output_dir, 'Story_2_Prescriptive_Bars.png')
plt.savefig(p2, dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(output_dir_path2, 'Story_2_Prescriptive_Bars.png'), dpi=300, bbox_inches='tight')
plt.close()

# ---------------------------------------------------------
# CHART 3: TẦM NHÌN VĨ MÔ (Line Chart 2012-2022)
# ---------------------------------------------------------
yearly_data_path = r"e:\project\datathon-2026-round-1\Path2\net_profit_by_category_yearly.csv"
if os.path.exists(yearly_data_path):
    ydf = pd.read_csv(yearly_data_path)
    # ydf columns: category, 2012, 2013, ... 2022
    years = [col for col in ydf.columns if str(col).isdigit()]
    
    fig, ax3 = plt.subplots(figsize=(14, 7))
    
    # Tạo dải màu cho tất cả các ngành hàng
    colors = sns.color_palette("husl", len(ydf))
    
    for idx, row in ydf.iterrows():
        cat = row['category']
        values = row[years].values.astype(float)
        
        color = colors[idx]
        linewidth = 3
        zorder = 5
        alpha = 0.85
            
        ax3.plot(years, values, color=color, linewidth=linewidth, zorder=zorder, alpha=alpha, label=cat)

    ax3.set_title('Xu hướng Lợi nhuận 10 năm của tất cả ngành hàng', fontsize=18, fontweight='bold', pad=20, loc='center', color='#1d3557')
    
    # Thêm Legend thay vì ghi chữ trực tiếp để tránh đè chữ
    ax3.legend(title='Ngành hàng', loc='center left', bbox_to_anchor=(1, 0.5), fontsize=12, title_fontsize=13, frameon=False)
    
    # Format Y-axis
    ax3.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{x*1e-6:,.0f}'.replace(',', '.') + ' Tr ₫'))
    ax3.tick_params(axis='y', colors='#888888')
    ax3.tick_params(axis='x', colors='#444444')
    
    # Decluttering
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.spines['left'].set_visible(False)
    ax3.spines['bottom'].set_color('#cccccc')
    ax3.grid(axis='y', color='#eeeeee', linestyle='-', linewidth=1)
    ax3.grid(axis='x', visible=False)
    
    plt.tight_layout()
    p3 = os.path.join(output_dir, 'Story_3_Historical_Trend.png')
    plt.savefig(p3, dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(output_dir_path2, 'Story_3_Historical_Trend.png'), dpi=300, bbox_inches='tight')
    plt.close()
