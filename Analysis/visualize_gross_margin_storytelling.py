import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import numpy as np
import os

data_dir = r"e:\project\datathon-2026-round-1"
out_dir = os.path.join(data_dir, "Path2", "Nop_Bai", "Hien")
csv_path = os.path.join(out_dir, "6_Gross_Margin_Data.csv")

try:
    monthly_data = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"Vui lòng đảm bảo file '{csv_path}' tồn tại.")
    exit()

# Chuyển đổi year_month_str sang datetime để vẽ biểu đồ
monthly_data['PlotDate'] = pd.to_datetime(monthly_data['year_month_str'], format='%Y-%m')

# 2. Thiết lập Biểu đồ Kể chuyện (Storytelling Chart)
fig, ax = plt.subplots(figsize=(20, 8), dpi=100)
fig.patch.set_facecolor('#fdfdfd') # Màu nền nhẹ

# Vẽ đường chính (Biên lợi nhuận gộp)
ax.plot(monthly_data['PlotDate'], monthly_data['gross_margin_pct'],
        color='#2c3e50',  # Màu xanh đen chuyên nghiệp
        linewidth=2.5,
        alpha=0.8,
        label='Biên Lợi Nhuận Gộp (%)')

# 3. Thêm các yếu tố kể chuyện (Storytelling Elements)

# 3.1. Thêm đường 0% và Vùng An toàn (10%-20%)
ax.axhline(0, color='black', linestyle='-', linewidth=1.5, alpha=0.5)
ax.axhspan(10, 20, color='#2ecc71', alpha=0.15, label='Vùng Lợi Nhuận An Toàn (10-20%)') # Xanh lá nhẹ

# 3.2. Đánh dấu và chú thích: Thủng đáy Tháng 8 (Năm lẻ) -> Chu kỳ giảm sâu nghiêm trọng
aug_odd_years = ['2013-08', '2015-08', '2017-08', '2019-08', '2021-08']
aug_points = monthly_data[monthly_data['year_month_str'].isin(aug_odd_years)]

ax.scatter(aug_points['PlotDate'], aug_points['gross_margin_pct'],
           color='#c0392b', s=150, zorder=5, edgecolor='black', linewidth=1,
           label='Sụt giảm nghiêm trọng (T8 năm lẻ)')

for i, point in aug_points.iterrows():
    ax.annotate(f"{point['gross_margin_pct']:.1f}%",
                xy=(point['PlotDate'], point['gross_margin_pct']),
                xytext=(0, -15),
                textcoords='offset points',
                ha='center', va='top',
                fontsize=11, fontweight='bold',
                color='#c0392b')

# 3.3. Đánh dấu và chú thích: Lỗ nặng Tháng 12 (Từ 2013 trở đi)
dec_points = monthly_data[(monthly_data['month'] == 12) & (monthly_data['year'] >= 2013)]

ax.scatter(dec_points['PlotDate'], dec_points['gross_margin_pct'],
           color='#f39c12', s=100, zorder=5, edgecolor='black', linewidth=1,
           label='Suy giảm định kỳ cuối năm (T12)')

for i, point in dec_points.iterrows():
    ax.annotate(f"{point['gross_margin_pct']:.1f}%",
                xy=(point['PlotDate'], point['gross_margin_pct']),
                xytext=(0, 12),
                textcoords='offset points',
                ha='center', va='bottom',
                fontsize=10, fontweight='bold',
                color='#d35400') # Darker orange for text

# 4. Định dạng Trục và Tiêu đề
# Tiêu đề Kể chuyện
plt.suptitle("Phân Tích Xu Hướng Biên Lợi Nhuận Gộp (Gross Margin) 2013-2022",
             fontsize=24, fontweight='bold', y=0.98)

# Định dạng trục X (Thời gian)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_minor_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.tick_params(axis='x', labelsize=12)

# Định dạng trục Y (%)
ax.set_ylabel("Biên Lợi Nhuận Gộp (%)", fontsize=14, fontweight='bold', labelpad=15)
ax.tick_params(axis='y', labelsize=12)
ax.set_ylim(-55, 35) # Thiết lập khoảng Y hợp lý

# Bật lưới
ax.grid(axis='y', linestyle='--', linewidth=0.5, color='#e0e0e0', alpha=0.7)

# Xóa viền biểu đồ thừa
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#dddddd')
ax.spines['bottom'].set_color('#dddddd')

# Hiển thị chú thích
ax.legend(fontsize=12, loc='lower left', frameon=True, fancybox=True, shadow=True, bbox_to_anchor=(0.02, 0.05))

plt.tight_layout(pad=3)
chart_path = os.path.join(out_dir, "6a_Gross_Margin_Trend.png")
plt.savefig(chart_path, dpi=300)
print(f"Improved chart saved to: {chart_path}")
plt.close()
