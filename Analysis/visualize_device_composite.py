import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# --- 1. Donut Chart (Device Share) ---
device_share = [45.1, 40.0, 14.9]
labels = ['Mobile', 'Desktop', 'Tablet']
colors_donut = ['#5DADE2', '#48C9B0', '#F39C12']

# Create a circle for the center of the donut chart
my_circle = plt.Circle((0,0), 0.6, color='white')
axes[0].pie(device_share, labels=labels, colors=colors_donut, autopct='%1.1f%%', startangle=90, pctdistance=0.8, textprops={'fontsize': 12, 'fontweight': 'bold', 'color': 'white'})
# Add the circle to the pie chart
axes[0].add_artist(my_circle)
axes[0].set_title('THIẾT BỊ ĐẶT HÀNG', fontsize=14, fontweight='bold', pad=15)
# Make labels outside bold and black
for text in axes[0].texts:
    if '%' not in text.get_text():
        text.set_color('black')
        text.set_fontsize(12)

# Data for bar charts
data = {
    'Device': ['Mobile', 'Desktop', 'Tablet'],
    'Avg_Session_Duration': [160, 85, 110], 
    'Drop_off_Rate': [68.5, 24.2, 35.8] 
}
df = pd.DataFrame(data)

# --- 2. Session Duration ---
colors_duration = ['#E74C3C', '#BDC3C7', '#BDC3C7']
sns.barplot(x='Device', y='Avg_Session_Duration', data=df, hue='Device', palette=colors_duration, ax=axes[1], legend=False)
axes[1].set_title('THỜI GIAN LƯU TRANG TRUNG BÌNH', fontsize=12, fontweight='bold', pad=10)
axes[1].set_ylabel('Thời gian (Giây)')
axes[1].set_xlabel('')
for p in axes[1].patches:
    height = p.get_height()
    if height > 0:
        axes[1].text(p.get_x() + p.get_width()/2., height + 2, f'{height:.0f}s', ha="center", fontsize=11, fontweight='bold')
axes[1].set_ylim(0, 200)

# Annotation arrow adjusted to not overlap
axes[1].annotate('Khoảng 107-213s', xy=(0, 172), xytext=(0, 192),
            arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
            ha='center', fontsize=10, color='#E74C3C', fontweight='bold')


# --- 3. Drop-off Rate ---
colors_dropoff = ['#8E44AD', '#BDC3C7', '#BDC3C7']
sns.barplot(x='Device', y='Drop_off_Rate', data=df, hue='Device', palette=colors_dropoff, ax=axes[2], legend=False)
axes[2].set_title('TỶ LỆ RỚT ĐƠN (DROP-OFF RATE)', fontsize=12, fontweight='bold', pad=10)
axes[2].set_ylabel('Tỷ lệ (%)')
axes[2].set_xlabel('')
for p in axes[2].patches:
    height = p.get_height()
    if height > 0:
        axes[2].text(p.get_x() + p.get_width()/2., height + 1, f'{height:.1f}%', ha="center", fontsize=11, fontweight='bold')
axes[2].set_ylim(0, 80)

# Annotation arrow adjusted to not overlap
axes[2].annotate('Điểm nghẽn thanh toán', xy=(0, 72.5), xytext=(0, 78),
            arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
            ha='center', fontsize=10, color='#8E44AD', fontweight='bold')

plt.tight_layout()

# Save
out_dir = r"e:\project\datathon-2026-round-1\Nop_bai\Images"
if not os.path.exists(out_dir):
    os.makedirs(out_dir)
out_path = os.path.join(out_dir, "5a_Device_Composite.png")
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Chart saved to {out_path}")
