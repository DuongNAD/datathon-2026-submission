import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# --- Cấu hình đường dẫn ---
data_dir = r"e:\project\datathon-2026-round-1"
out_dir = os.path.join(data_dir, "Path2", "Nop_Bai", "Hien")
csv_path = os.path.join(out_dir, "8_Customer_Tier_Data.csv")
chart_path = os.path.join(out_dir, "8_Customer_Tier_Behavior.png")

# --- 1. Đọc dữ liệu ---
df = pd.read_csv(csv_path)

tiers = df['Tier'].tolist()
percentages = df['Percentage'].tolist()
aov_values = df['AOV'].tolist()

colors_storytelling = ['#bdc3c7', '#95a5a6', '#f39c12', '#8e44ad']

# --- 2. Tạo Figure (Biểu đồ 2 trục / Dual-Axis) ---
fig, ax1 = plt.subplots(figsize=(11, 7), dpi=150)
fig.patch.set_facecolor('#fdfdfd')
ax1.set_facecolor('#fdfdfd')

x_pos = np.arange(len(tiers))

# =============================================================
# TRỤC TRÁI (BAR CHART) - GIÁ TRỊ ĐƠN HÀNG
# =============================================================
bars = ax1.bar(x_pos, aov_values, color=colors_storytelling, width=0.5, alpha=0.9)

# Thêm Data Labels cho Bar Chart
for i, bar in enumerate(bars):
    height = bar.get_height()
    formatted_height = f"{int(height):,}".replace(",", ".")
    ax1.annotate(f"{formatted_height} VNĐ",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 8),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=14, fontweight='bold', color=colors_storytelling[i],
                bbox=dict(facecolor='#fdfdfd', edgecolor='none', pad=2))

# =============================================================
# TRỤC PHẢI (LINE CHART) - TỶ TRỌNG KHÁCH HÀNG
# =============================================================
ax2 = ax1.twinx()
line = ax2.plot(x_pos, percentages, color='#e74c3c', marker='o', markersize=10, linewidth=3, linestyle='-')

# Thêm Data Labels cho Line Chart
for i, txt in enumerate(percentages):
    # Đẩy label của line chart lên trên một chút để không đè vào đường thẳng
    ax2.annotate(f"{txt}%", 
                 xy=(x_pos[i], percentages[i]), 
                 xytext=(0, 12), 
                 textcoords="offset points", 
                 ha='center', va='bottom', fontsize=15, fontweight='bold', color='#c0392b',
                 bbox=dict(facecolor='#fdfdfd', edgecolor='none', pad=2))

# Chú thích ngay trên biểu đồ thay vì dùng Legend (Bỏ đi vì đã dùng Y-label)

from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# Thêm Legend (Chú thích)
legend_elements = [
    Patch(facecolor='#95a5a6', alpha=0.9, label='Giá trị trung bình đơn (Cột)'),
    Line2D([0], [0], color='#e74c3c', lw=3, marker='o', markersize=10, label='Tỷ trọng khách hàng (Đường)')
]
ax1.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=2, frameon=False, fontsize=13)

# =============================================================
# ĐỊNH DẠNG CHUNG
# =============================================================
# Set limits để chừa không gian và tránh overlap
ax1.set_ylim(0, 60000)
ax2.set_ylim(0, 100)

ax1.set_xticks(x_pos)
tiers_with_desc = [
    "Khách Mới\n(Tỷ lệ giữ chân thấp)",
    "Khách Bạc\n(Có thói quen mua lại)",
    "Khách Vàng\n(Lợi nhuận chủ lực)",
    "Khách Kim Cương\n(Nguồn thu lớn nhất)"
]
ax1.set_xticklabels(tiers_with_desc, fontsize=13, fontweight='bold')

# Thêm trục tọa độ Y (Thang đo)
ax1.set_yticks(np.arange(0, 70000, 10000))
ax1.set_yticklabels([f"{int(y):,}".replace(",", ".") if y > 0 else "0" for y in np.arange(0, 70000, 10000)], fontsize=12, color='#2c3e50')
ax2.set_yticks(np.arange(0, 110, 20))
ax2.set_yticklabels([f"{y}%" if y > 0 else "0" for y in np.arange(0, 110, 20)], fontsize=12, color='#c0392b')

# Thêm nhãn trục Y
ax1.set_ylabel("Giá trị trung bình đơn (VNĐ)", fontsize=13, fontweight='bold', color='#2c3e50', labelpad=10)
ax2.set_ylabel("Tỷ trọng khách hàng (%)", fontsize=13, fontweight='bold', color='#c0392b', labelpad=10)

# Hiện đường viền bên trái và phải
ax1.spines['left'].set_visible(True)
ax1.spines['left'].set_color('#dddddd')
ax2.spines['right'].set_visible(True)
ax2.spines['right'].set_color('#dddddd')

# Thêm Grid cho dễ gióng hàng
ax1.grid(axis='y', linestyle='--', alpha=0.3)

# Ẩn viền trên
ax1.spines['top'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax1.spines['bottom'].set_color('#dddddd')
ax1.spines['bottom'].set_linewidth(1.5)
ax2.spines['bottom'].set_visible(False)
ax2.spines['left'].set_visible(False)

# Chú thích ngay trên biểu đồ (Bỏ bớt vì trục Y đã có label rõ ràng)
# Xóa các dòng ax1.text và ax2.text cũ

plt.title("Chênh lệch AOV giữa các Phân tầng Khách hàng", fontsize=16, fontweight='bold', color='#2c3e50', pad=45)

# --- 3. Lưu ảnh ---
plt.tight_layout()
plt.savefig(chart_path, dpi=300, bbox_inches='tight')
print(f"Chart saved to: {chart_path}")
plt.close()
