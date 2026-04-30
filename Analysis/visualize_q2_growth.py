import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Data for the chart based on the text
data = {
    'Danh mục': ['Streetwear', 'GenZ'],
    'Tăng trưởng (%)': [81.0, 92.0]
}
df = pd.DataFrame(data)

# Aesthetics
sns.set_theme(style="whitegrid")
plt.figure(figsize=(6, 5))

# Plotting
colors = ['#FF7F50', '#2E86C1'] # Coral for Streetwear, Blue for GenZ
ax = sns.barplot(x='Danh mục', y='Tăng trưởng (%)', data=df, palette=colors)

plt.title("TĂNG TRƯỞNG DOANH THU QUÝ 2\n(So với trung bình các tháng khác)", fontsize=14, fontweight='bold', pad=15)
plt.ylabel("Tốc độ tăng trưởng (%)", fontsize=12)
plt.xlabel("")
plt.ylim(0, 110)

# Add value labels
for p in ax.patches:
    height = p.get_height()
    ax.text(p.get_x() + p.get_width()/2., height + 2, f'+{height:.0f}%', ha="center", fontsize=14, fontweight='bold', color='#c0392b')

plt.tight_layout()

# Save chart
out_dir = r"e:\project\datathon-2026-round-1\Nop_bai\Images"
if not os.path.exists(out_dir):
    os.makedirs(out_dir)
out_path = os.path.join(out_dir, "4c_Category_Growth_Q2.png")
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Chart saved to {out_path}")
