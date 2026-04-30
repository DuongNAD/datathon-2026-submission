import pandas as pd
import matplotlib.pyplot as plt
import os

data_dir = r"e:\project\datathon-2026-round-1"
out_dir = os.path.join(data_dir, "Path2", "Nop_Bai", "Hien")
csv_path = os.path.join(out_dir, "6b_Gross_Margin_Seasonality_Data.csv")

# 1. Đọc dữ liệu Pivot đã được tạo sẵn
pivot_data = pd.read_csv(csv_path, index_col='month')
# Chuyển đổi tên cột (năm) thành số nguyên
pivot_data.columns = pivot_data.columns.astype(int)

# Bỏ năm 2012 vì là năm không trọn vẹn (chỉ có 6 tháng cuối năm) 
# và chưa hình thành chu kỳ kinh doanh như các năm sau, tạo ra một đường thẳng ngang gây nhiễu.
if 2012 in pivot_data.columns:
    pivot_data = pivot_data.drop(columns=[2012])

# 2. Visualization (Trực quan hóa dữ liệu Storytelling)
fig, ax = plt.subplots(figsize=(16, 8), dpi=120)
fig.patch.set_facecolor('#fdfdfd')
ax.set_facecolor('#fdfdfd')

# Thêm Vertical Span (Bôi nền dọc) để tăng Focus vào T8 và T12
ax.axvspan(7.8, 8.2, color='#c0392b', alpha=0.05)
ax.axvspan(11.8, 12.2, color='#f39c12', alpha=0.05)

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
odd_years_dip = [2013, 2015, 2017, 2019, 2021]

# Vẽ từng đường cho mỗi năm
for year in pivot_data.columns:
    if year in odd_years_dip:
        # Highlight các năm lẻ bị thủng đáy
        ax.plot(pivot_data.index, pivot_data[year], color='#c0392b', linewidth=2.5, alpha=0.9)
        # Đánh dấu (marker) riêng điểm tháng 8
        ax.scatter(8, pivot_data.loc[8, year], color='#c0392b', s=150, zorder=6, edgecolor='white')
        # Đánh dấu điểm tháng 12 (lỗ nặng định kỳ) với viền đỏ, lõi cam để tạo tính liên kết
        ax.scatter(12, pivot_data.loc[12, year], facecolor='#f39c12', edgecolor='#c0392b', linewidth=2, s=120, zorder=6)
    else:
        # Background noise (Các năm chẵn bình thường)
        ax.plot(pivot_data.index, pivot_data[year], color='#7f8c8d', linewidth=1.5, alpha=0.6)
        # Đánh dấu điểm tháng 12 cho tất cả các năm từ 2013 trở đi
        if year >= 2013:
            ax.scatter(12, pivot_data.loc[12, year], color='#f39c12', s=120, zorder=5, edgecolor='white')

# 3. Add Annotations (Thêm chú thích)
ax.annotate('Suy giảm lợi nhuận nghiêm trọng\nTháng 8 (Chu kỳ 2 năm)',
            xy=(8, -35), xytext=(7.5, -45),
            ha='right', va='top', fontsize=12, fontweight='bold', color='#c0392b',
            arrowprops=dict(arrowstyle='->', color='#c0392b', lw=1.5))

ax.annotate('Sụt giảm biên lợi nhuận định kỳ\nTháng 12 hàng năm',
            xy=(12, -25), xytext=(11.5, -40),
            ha='right', va='top', fontsize=12, fontweight='bold', color='#f39c12',
            arrowprops=dict(arrowstyle='->', color='#f39c12', lw=1.5))

# 4. Formatting (Định dạng)
plt.title("Tính Mùa Vụ Của Biên Lợi Nhuận Gộp (2013-2022)", fontsize=20, fontweight='bold', pad=20)

ax.set_xticks(range(1, 13))
ax.set_xticklabels(months, fontsize=12)
ax.set_ylim(-55, 30) # Cấp thêm không gian trống phía dưới để chữ không đè vào trục X
ax.set_ylabel("Gross Margin (%)", fontsize=12, fontweight='bold')
ax.tick_params(axis='y', labelsize=11)

ax.axhline(0, color='#2c3e50', linestyle='--', linewidth=1.5, alpha=0.7)
ax.grid(axis='y', linestyle='--', alpha=0.5)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Tạo Custom Legend
from matplotlib.lines import Line2D
custom_lines = [
    Line2D([0], [0], color='#c0392b', lw=2.5, marker='o', markersize=8, markerfacecolor='#c0392b', markeredgecolor='white'),
    Line2D([0], [0], color='#f39c12', lw=2, marker='o', markersize=8, markerfacecolor='#f39c12', markeredgecolor='white'),
    Line2D([0], [0], color='#7f8c8d', lw=1.5)
]
ax.legend(custom_lines, [
    'Năm lẻ (Chu kỳ suy giảm T8)', 
    'Suy giảm định kỳ (T12 hàng năm)', 
    'Biến động bình thường (Năm chẵn)'
], loc='lower left', fontsize=11, frameon=True, bbox_to_anchor=(0.02, 0.05))

plt.tight_layout()
chart_path = os.path.join(out_dir, "6b_Gross_Margin_Seasonality.png")
plt.savefig(chart_path, dpi=300)
print(f"Improved seasonality chart saved to: {chart_path}")
plt.close()
