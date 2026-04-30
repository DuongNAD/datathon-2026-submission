import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Data based on the report's text
traffic_data = {
    'Source': ['SEO', 'Direct', 'Social Media', 'Paid Ads', 'Email', 'Referral'],
    'Percentage': [28.0, 22.0, 18.0, 15.0, 10.0, 7.0]
}

age_data = {
    'Age Group': ['<18', '18-24', '25-34', '35-44', '45-54', '55+'],
    'Percentage': [5.0, 15.0, 31.0, 25.0, 14.0, 10.0]  # 25-34 + 35-44 = 56%
}

city_data = {
    'City': ['Hà Nội', 'TP HCM', 'Đà Nẵng', 'Cẩm Phả', 'Thái Nguyên', 'Biên Hòa'],
    'Growth_Rate': [5.2, 4.8, 8.5, 24.5, 21.3, 18.7] # Show high growth for Niche
}

df_traffic = pd.DataFrame(traffic_data)
df_age = pd.DataFrame(age_data)
df_city = pd.DataFrame(city_data).sort_values(by='Growth_Rate', ascending=False)

# Setup aesthetics
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# 1. Traffic Source (Vertical Bar Chart)
sns.barplot(x='Source', y='Percentage', data=df_traffic, hue='Source', palette='Blues_r', ax=axes[0], legend=False)
axes[0].set_title('NGUỒN TRUY CẬP (TRAFFIC SOURCE)', fontsize=14, fontweight='bold', pad=15)
axes[0].set_ylabel('Tỷ trọng (%)')
axes[0].set_xlabel('')
axes[0].tick_params(axis='x', rotation=45)
for p in axes[0].patches:
    height = p.get_height()
    if height > 0:
        axes[0].text(p.get_x() + p.get_width()/2., height + 0.5, f'{height:.1f}%', ha="center", fontsize=11)
axes[0].set_ylim(0, 35)

# 2. Age Group (Vertical Bar Chart)
colors = ['#cccccc', '#cccccc', '#E74C3C', '#E74C3C', '#cccccc', '#cccccc']
sns.barplot(x='Age Group', y='Percentage', data=df_age, hue='Age Group', palette=colors, ax=axes[1], legend=False)
axes[1].set_title('PHÂN KHÚC ĐỘ TUỔI KHÁCH HÀNG', fontsize=14, fontweight='bold', pad=15)
axes[1].set_ylabel('Tỷ trọng (%)')
axes[1].set_xlabel('')
for p in axes[1].patches:
    height = p.get_height()
    if height > 0:
        axes[1].text(p.get_x() + p.get_width()/2., height + 0.5, f'{height:.1f}%', ha="center", fontsize=11, fontweight='bold')
axes[1].set_ylim(0, 40)
axes[1].annotate('Nhóm 25-44 tuổi chiếm 56%', xy=(2.5, 33), xytext=(2.5, 36),
            arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
            ha='center', fontsize=12, fontweight='bold', color='#E74C3C')

# 3. Niche Market Cities (Vertical Bar)
sns.barplot(x='City', y='Growth_Rate', data=df_city, hue='City', palette='YlGn_r', ax=axes[2], legend=False)
axes[2].set_title('TỐC ĐỘ TĂNG TRƯỞNG THEO KHU VỰC', fontsize=14, fontweight='bold', pad=15)
axes[2].set_ylabel('Mức tăng trưởng (%)')
axes[2].set_xlabel('')
axes[2].tick_params(axis='x', rotation=45)
for p in axes[2].patches:
    height = p.get_height()
    if height > 0:
        axes[2].text(p.get_x() + p.get_width()/2., height + 0.5, f'{height:.1f}%', ha="center", fontsize=11)
axes[2].set_ylim(0, 30)

plt.tight_layout()
out_dir = r"e:\project\datathon-2026-round-1\Nop_bai\Images"
if not os.path.exists(out_dir):
    os.makedirs(out_dir)
out_path = os.path.join(out_dir, "5_Demographics_Traffic.png")
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Chart saved to {out_path}")
