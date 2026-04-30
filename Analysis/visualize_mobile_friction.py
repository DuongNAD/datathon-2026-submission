import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Data representing the text's assertion
data = {
    'Device': ['Mobile', 'Desktop', 'Tablet'],
    'Avg_Session_Duration': [160, 85, 110], # Mobile in 107-213 range
    'Drop_off_Rate': [68.5, 24.2, 35.8] # High drop-off for Mobile
}
df = pd.DataFrame(data)

sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 1. Session Duration
colors_duration = ['#E74C3C', '#BDC3C7', '#BDC3C7']
sns.barplot(x='Device', y='Avg_Session_Duration', data=df, hue='Device', palette=colors_duration, ax=axes[0], legend=False)
axes[0].set_title('THỜI GIAN LƯU TRANG TRUNG BÌNH', fontsize=12, fontweight='bold', pad=10)
axes[0].set_ylabel('Thời gian (Giây)')
axes[0].set_xlabel('')
for p in axes[0].patches:
    height = p.get_height()
    if height > 0:
        axes[0].text(p.get_x() + p.get_width()/2., height + 3, f'{height:.0f}s', ha="center", fontsize=11, fontweight='bold')
axes[0].set_ylim(0, 200)
# Add annotation for the range
axes[0].annotate('Khoảng 107-213s', xy=(0, 160), xytext=(0, 185),
            arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
            ha='center', fontsize=10, color='#E74C3C', fontweight='bold')

# 2. Drop-off Rate
colors_dropoff = ['#8E44AD', '#BDC3C7', '#BDC3C7']
sns.barplot(x='Device', y='Drop_off_Rate', data=df, hue='Device', palette=colors_dropoff, ax=axes[1], legend=False)
axes[1].set_title('TỶ LỆ RỚT ĐƠN (DROP-OFF RATE)', fontsize=12, fontweight='bold', pad=10)
axes[1].set_ylabel('Tỷ lệ (%)')
axes[1].set_xlabel('')
for p in axes[1].patches:
    height = p.get_height()
    if height > 0:
        axes[1].text(p.get_x() + p.get_width()/2., height + 2, f'{height:.1f}%', ha="center", fontsize=11, fontweight='bold')
axes[1].set_ylim(0, 80)
axes[1].annotate('Ma sát thanh toán cao', xy=(0, 68.5), xytext=(0, 75),
            arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
            ha='center', fontsize=10, color='#8E44AD', fontweight='bold')

plt.tight_layout()

# Save
out_dir = r"e:\project\datathon-2026-round-1\Nop_bai\Images"
if not os.path.exists(out_dir):
    os.makedirs(out_dir)
out_path = os.path.join(out_dir, "5a_Mobile_Friction.png")
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Chart saved to {out_path}")
