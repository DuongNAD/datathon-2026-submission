import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.patches import Patch

# --- Cấu hình đường dẫn ---
data_dir = r"e:\project\datathon-2026-round-1"
out_dir = os.path.join(data_dir, "Path2", "Nop_Bai", "Hien")
csv_path = os.path.join(out_dir, "7_AOV_Promotion_Data.csv")
chart_a_path = os.path.join(out_dir, "7a_Promotion_Volume.png")
chart_b_path = os.path.join(out_dir, "7b_Promotion_AOV.png")

# --- 1. Đọc dữ liệu ---
df = pd.read_csv(csv_path)

# Trích xuất các con số
total_aov = df.loc[df['Category'] == 'Toàn Sàn', 'AOV'].values[0]

no_promo_orders = df.loc[df['Category'] == 'Không Khuyến Mãi', 'Total_Orders'].values[0]
no_promo_pct = df.loc[df['Category'] == 'Không Khuyến Mãi', 'Percentage'].values[0]
no_promo_aov = df.loc[df['Category'] == 'Không Khuyến Mãi', 'AOV'].values[0]

promo_orders = df.loc[df['Category'] == 'Có Khuyến Mãi', 'Total_Orders'].values[0]
promo_pct = df.loc[df['Category'] == 'Có Khuyến Mãi', 'Percentage'].values[0]
promo_aov = df.loc[df['Category'] == 'Có Khuyến Mãi', 'AOV'].values[0]

# Định nghĩa màu sắc
color_no_promo = '#2c3e50' # Xanh Navy chuyên nghiệp (Bình thường)
color_promo = '#e74c3c'    # Đỏ cảnh báo (Khuyến mãi kéo tụt AOV)

# =============================================================
# CHART 7A: TỶ TRỌNG ĐƠN HÀNG (DONUT CHART)
# =============================================================
fig1, ax1 = plt.subplots(figsize=(9, 8), dpi=150)
fig1.patch.set_facecolor('#fdfdfd')
ax1.set_facecolor('#fdfdfd')

labels = ['Có sử dụng\nKhuyến Mãi\n(Săn Deal)', 'Không dùng\nKhuyến Mãi\n(Mua Thông Thường)']
sizes = [promo_orders, no_promo_orders]
colors = [color_promo, color_no_promo]
explode = (0.05, 0) # Tách phần Promo ra một chút

wedges, texts, autotexts = ax1.pie(sizes, explode=explode, labels=labels, colors=colors, 
                                   autopct='%1.1f%%', startangle=140, pctdistance=0.8,
                                   textprops=dict(color="black", fontsize=14, fontweight='bold'),
                                   wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2))

# Chỉnh màu chữ bên trong Donut
autotexts[0].set_color('white')
autotexts[0].set_fontsize(20)
autotexts[1].set_color('white')
autotexts[1].set_fontsize(20)

# Center text
ax1.text(0, 0, f"Tổng\n646,945\nĐơn", ha='center', va='center', fontsize=22, fontweight='bold', color='#333333')

plt.title("TỶ TRỌNG ĐƠN HÀNG SỬ DỤNG KHUYẾN MÃI", fontsize=20, fontweight='bold', color='#2c3e50', pad=40)

# Thêm Legend
legend_elements_1 = [
    Patch(facecolor=color_no_promo, edgecolor='none', label='Mua Thông Thường'),
    Patch(facecolor=color_promo, edgecolor='none', label='Săn Deal (Khuyến Mãi)')
]
ax1.legend(handles=legend_elements_1, loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False, fontsize=12)

plt.tight_layout()
plt.savefig(chart_a_path, dpi=300, bbox_inches='tight')
print(f"Chart 7A saved to: {chart_a_path}")
plt.close(fig1)


# =============================================================
# CHART 7B: GIÁ TRỊ TRUNG BÌNH ĐƠN (BAR CHART)
# =============================================================
fig2, ax2 = plt.subplots(figsize=(9, 8), dpi=150)
fig2.patch.set_facecolor('#fdfdfd')
ax2.set_facecolor('#fdfdfd')

categories = ['Mua Thông Thường\n(Không Khuyến Mãi)', 'Nhóm Săn Deal\n(Có Khuyến Mãi)']
aov_values = [no_promo_aov, promo_aov]
bar_colors = [color_no_promo, color_promo]

bars = ax2.bar(categories, aov_values, color=bar_colors, width=0.5, edgecolor='white', linewidth=2)

# Thêm số liệu lên đỉnh cột
for bar in bars:
    height = bar.get_height()
    ax2.annotate(f"{int(height):,} VNĐ",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 5),  # offset points
                textcoords="offset points",
                ha='center', va='bottom', fontsize=16, fontweight='bold', color=bar.get_facecolor())

# Baseline cho Total AOV
ax2.axhline(total_aov, color='#7f8c8d', linestyle='--', linewidth=2, alpha=0.8, zorder=0)
ax2.text(1.5, total_aov, f"Trung bình toàn sàn\n{int(total_aov):,} VNĐ", 
         ha='center', va='center', fontsize=12, fontweight='bold', color='#7f8c8d',
         bbox=dict(facecolor='white', edgecolor='none', alpha=0.8))

# Tính chênh lệch AOV
drop_pct = ((no_promo_aov - promo_aov) / no_promo_aov) * 100

# Thể hiện chênh lệch độ cao (Chuyên nghiệp hơn, không đè chữ)
# Đường ngang từ cột Không khuyến mãi ra giữa
ax2.plot([0.25, 0.5], [no_promo_aov, no_promo_aov], color='#c0392b', linestyle=':', linewidth=2)
# Đường ngang từ cột Có khuyến mãi ra giữa
ax2.plot([0.75, 0.5], [promo_aov, promo_aov], color='#c0392b', linestyle=':', linewidth=2)
# Mũi tên dọc thể hiện khoảng rơi (Height difference) - 2 đầu
ax2.annotate('', xy=(0.5, promo_aov), xytext=(0.5, no_promo_aov),
            arrowprops=dict(arrowstyle='<->', color='#c0392b', lw=2.5))
# Text nằm cạnh mũi tên, hoàn toàn lọt thỏm trong không gian trắng
ax2.text(0.53, (no_promo_aov + promo_aov) / 2, f"Giá trị trung bình đơn\ngiảm {drop_pct:.1f}%",
        ha='left', va='center', fontsize=13, fontweight='bold', color='#c0392b',
        bbox=dict(facecolor='#fdfdfd', edgecolor='none', pad=3))

# Định dạng trục
ax2.set_ylim(0, 32000)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_color('#dddddd')
ax2.spines['bottom'].set_linewidth(1.5)
ax2.tick_params(axis='y', labelsize=12)
ax2.tick_params(axis='x', labelsize=14)
ax2.grid(axis='y', linestyle='--', alpha=0.3)

plt.title("SO SÁNH GIÁ TRỊ TRUNG BÌNH ĐƠN HÀNG", fontsize=20, fontweight='bold', color='#2c3e50', pad=40)

# Thêm Legend
legend_elements_2 = [
    Patch(facecolor=color_no_promo, edgecolor='none', label='Mua Thông Thường'),
    Patch(facecolor=color_promo, edgecolor='none', label='Săn Deal (Khuyến Mãi)')
]
ax2.legend(handles=legend_elements_2, loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=2, frameon=False, fontsize=12)

plt.tight_layout()
plt.savefig(chart_b_path, dpi=300, bbox_inches='tight')
print(f"Chart 7B saved to: {chart_b_path}")
plt.close(fig2)
