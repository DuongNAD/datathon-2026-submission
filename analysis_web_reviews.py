import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configure plot style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("muted")

os.makedirs('Nop_bai/Images', exist_ok=True)

print("Reading data...")
web = pd.read_csv('web_traffic.csv')
web['date'] = pd.to_datetime(web['date'])
orders = pd.read_csv('orders.csv')
orders['order_date'] = pd.to_datetime(orders['order_date'])

# 1. Conversion Funnel Analysis
daily_orders = orders.groupby('order_date').size().reset_index(name='total_orders')
df_funnel = pd.merge(web, daily_orders, left_on='date', right_on='order_date', how='left')
df_funnel['total_orders'] = df_funnel['total_orders'].fillna(0)

# Aggregate by Month-Year
df_funnel['month_year'] = df_funnel['date'].dt.to_period('M')
monthly_funnel = df_funnel.groupby('month_year').agg({
    'sessions': 'sum',
    'page_views': 'sum',
    'total_orders': 'sum'
}).reset_index()
monthly_funnel['conversion_rate'] = (monthly_funnel['total_orders'] / monthly_funnel['sessions']) * 100
monthly_funnel['month_year'] = monthly_funnel['month_year'].astype(str)

fig, ax1 = plt.subplots(figsize=(14, 7))

# Bar chart for Sessions
ax1.bar(monthly_funnel['month_year'], monthly_funnel['sessions'], color='#8bb0d9', alpha=0.8, label='Lượng Truy Cập')
ax1.set_xlabel('Tháng', fontsize=12, fontweight='bold')
ax1.set_ylabel('Lượng Truy Cập', color='#2b6ca3', fontsize=12, fontweight='bold')

# Display every 3rd month on x-axis to prevent text overlap
xticks = range(0, len(monthly_funnel['month_year']), 3)
xticklabels = monthly_funnel['month_year'].iloc[xticks]
ax1.set_xticks(xticks)
ax1.set_xticklabels(xticklabels, rotation=45)

ax1.grid(axis='y', linestyle='--', alpha=0.6)

# Line chart for Conversion Rate
ax2 = ax1.twinx()
ax2.plot(monthly_funnel['month_year'], monthly_funnel['conversion_rate'], color='#d9534f', marker='o', linewidth=3, markersize=8, label='Tỉ lệ chuyển đổi (%)')
ax2.set_ylabel('Tỷ lệ Chuyển Đổi (%)', color='#d9534f', fontsize=12, fontweight='bold')

plt.title('Lượng Truy Cập & Tỷ Lệ Chuyển Đổi Theo Tháng', fontsize=16, fontweight='bold', pad=20)
fig.legend(loc="upper left", bbox_to_anchor=(0.12,0.88), fontsize=11, frameon=True)
plt.tight_layout()
plt.savefig('Nop_bai/Images/5_Conversion_Funnel.png', dpi=300)
plt.close()
print("Saved Conversion Funnel chart (5_Conversion_Funnel.png).")

# 2. Sentiment Analysis from Reviews
print("Reading reviews...")
reviews = pd.read_csv('reviews.csv')
bad_reviews = reviews[reviews['rating'] <= 2].copy()

# Since the review dataset only contains short phrases in review_title, we count their frequencies
bad_titles = bad_reviews['review_title'].dropna().str.strip()
title_counts = bad_titles.value_counts().head(8).reset_index()
title_counts.columns = ['Phân loại đánh giá', 'Số lượng']

# Map English phrases to Vietnamese concepts to match the report's business context 
# based on the image's requirement ("chậm", "size không chuẩn"...)
vi_mapping = {
    'Poor quality': 'Chất lượng kém',
    'Below expectations': 'Dưới mức kỳ vọng',
    'Would not recommend': 'Không khuyến khích mua',
    'Very disappointed': 'Rất thất vọng',
    'Not as described': 'Không đúng mô tả',
    'Some issues': 'Gặp một số vấn đề',
    'Would not reorder': 'Sẽ không mua lại'
}
title_counts['Nhóm vấn đề'] = title_counts['Phân loại đánh giá'].map(vi_mapping).fillna(title_counts['Phân loại đánh giá'])

plt.figure(figsize=(12, 6))
ax = sns.barplot(x='Số lượng', y='Nhóm vấn đề', data=title_counts, palette='Reds_r')

# Add annotations
for i, v in enumerate(title_counts['Số lượng']):
    ax.text(v + 100, i, str(v), color='black', va='center', fontweight='bold')

plt.title('Các Cụm Từ Khoá Thường Gặp Nhất Trong Đánh Giá 1-2 Sao (Sentiment Analysis)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Số lượng lượt đề cập', fontsize=12)
plt.ylabel('Vấn đề Khách Hàng (Keywords)', fontsize=12)
plt.xlim(0, max(title_counts['Số lượng']) * 1.15)
plt.tight_layout()
plt.savefig('Nop_bai/Images/6_Bad_Reviews_Keywords.png', dpi=300)
plt.close()
print("Saved Sentiment Analysis chart (6_Bad_Reviews_Keywords.png).")
