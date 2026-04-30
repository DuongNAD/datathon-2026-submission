import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

plt.rcParams['font.size'] = 12
os.makedirs('Nop_bai/Images', exist_ok=True)

# ============================================================
# Load & merge data
# ============================================================
print("Loading data...")
customers = pd.read_csv('customers.csv')
customers['signup_date'] = pd.to_datetime(customers['signup_date'])
geography = pd.read_csv('geography.csv')
orders = pd.read_csv('orders.csv')
orders['order_date'] = pd.to_datetime(orders['order_date'])
sales = pd.read_csv('train_model/dataset/sales_train.csv')

# Merge customer with geography (via zip)
cust_geo = customers.merge(geography[['zip', 'region']].drop_duplicates(), on='zip', how='left')

# Merge orders with customer info
orders_full = orders.merge(cust_geo[['customer_id', 'age_group', 'acquisition_channel', 'region', 'city', 'signup_date']], on='customer_id', how='left')

# ============================================================
# 1. MARKET PENETRATION BY REGION
#    New vs Returning customers per region
# ============================================================
print("[1/2] Market Penetration by Region...")

# Determine first order date per customer
first_order = orders_full.groupby('customer_id')['order_date'].min().reset_index()
first_order.columns = ['customer_id', 'first_order_date']
orders_full = orders_full.merge(first_order, on='customer_id', how='left')

# A customer is "New" on a given order if it's their first order, otherwise "Returning"
orders_full['customer_type'] = np.where(
    orders_full['order_date'] == orders_full['first_order_date'],
    'Khách Mới', 'Khách Quay Lại'
)

# Count by region and customer type
region_vi = {'East': 'Miền Đông', 'Central': 'Miền Trung', 'West': 'Miền Tây'}
orders_full['region_vi'] = orders_full['region'].map(region_vi).fillna('Không xác định')

region_type = orders_full.groupby(['region_vi', 'customer_type']).size().reset_index(name='order_count')
region_pivot = region_type.pivot(index='region_vi', columns='customer_type', values='order_count').fillna(0)
region_pivot['total'] = region_pivot.sum(axis=1)
region_pivot = region_pivot.sort_values('total', ascending=True)

# Calculate returning rate
region_pivot['returning_rate'] = region_pivot['Khách Quay Lại'] / region_pivot['total'] * 100

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), gridspec_kw={'width_ratios': [3, 2]})

# Left: Stacked horizontal bar
cols_to_plot = ['Khách Mới', 'Khách Quay Lại']
colors = ['#3498db', '#e74c3c']
region_pivot[cols_to_plot].plot(kind='barh', stacked=True, ax=ax1, color=colors, edgecolor='white', linewidth=0.5)
ax1.set_xlabel('Số lượng Đơn hàng', fontsize=12, fontweight='bold')
ax1.set_ylabel('')
ax1.set_title('Phân Bố Khách Mới & Khách Quay Lại\nTheo Khu Vực', fontsize=14, fontweight='bold')
ax1.legend(title='Loại Khách Hàng', fontsize=10, title_fontsize=11)
ax1.grid(axis='x', linestyle='--', alpha=0.4)
ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
ax1.set_xlim(0, region_pivot['total'].max() * 1.2)

# Add total labels
for i, (idx, row) in enumerate(region_pivot.iterrows()):
    ax1.text(row['total'] + 4000, i, f'{row["total"]:,.0f}', va='center', fontweight='bold', fontsize=11)

# Right: Returning rate bar
bars = ax2.barh(region_pivot.index, region_pivot['returning_rate'], color='#e74c3c', alpha=0.85, edgecolor='white')
ax2.set_xlabel('Tỷ lệ Khách Quay Lại (%)', fontsize=12, fontweight='bold')
ax2.set_title('Tỷ Lệ Giữ Chân\nTheo Khu Vực', fontsize=14, fontweight='bold')
ax2.set_xlim(0, 100)
ax2.grid(axis='x', linestyle='--', alpha=0.4)

for bar, val in zip(bars, region_pivot['returning_rate']):
    ax2.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f'{val:.1f}%',
             va='center', fontweight='bold', fontsize=12, color='#c0392b')

plt.tight_layout()
plt.savefig('Nop_bai/Images/11a_Market_Penetration_Region.png', dpi=300)
plt.close()
print("   -> Saved 11a_Market_Penetration_Region.png")

# ============================================================
# 2. CLV BY AGE SEGMENT + ACQUISITION CHANNEL
# ============================================================
print("[2/2] CLV by Age Segment & Acquisition Channel...")

# CLV proxy = total number of orders per customer (since we don't have direct revenue per customer)
# Better: count orders AND calculate average orders per customer per segment
clv_age = orders_full.groupby(['customer_id', 'age_group']).size().reset_index(name='total_orders')
clv_by_age = clv_age.groupby('age_group').agg(
    avg_orders=('total_orders', 'mean'),
    total_customers=('customer_id', 'nunique'),
    total_orders_sum=('total_orders', 'sum')
).reset_index()
clv_by_age = clv_by_age.sort_values('avg_orders', ascending=False)

# Age group order
age_order = ['18-24', '25-34', '35-44', '45-54', '55+']
clv_by_age['age_group'] = pd.Categorical(clv_by_age['age_group'], categories=age_order, ordered=True)
clv_by_age = clv_by_age.sort_values('age_group')

# CLV by acquisition channel
clv_channel = orders_full.groupby(['customer_id', 'acquisition_channel']).size().reset_index(name='total_orders')
clv_by_channel = clv_channel.groupby('acquisition_channel').agg(
    avg_orders=('total_orders', 'mean'),
    total_customers=('customer_id', 'nunique')
).reset_index()
clv_by_channel = clv_by_channel.sort_values('avg_orders', ascending=False)

channel_vi = {
    'organic_search': 'Organic Search',
    'paid_search': 'Paid Search',
    'social_media': 'Social Media',
    'email_campaign': 'Email Campaign',
    'referral': 'Referral',
    'direct': 'Direct'
}
clv_by_channel['channel_label'] = clv_by_channel['acquisition_channel'].map(channel_vi)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Left: CLV by Age
bar_colors_age = ['#f39c12', '#e74c3c', '#e74c3c', '#3498db', '#3498db']
# Highlight the top CLV age group
max_clv_age = clv_by_age['avg_orders'].max()
bar_colors_age = ['#e74c3c' if v == max_clv_age else '#3498db' for v in clv_by_age['avg_orders']]

bars1 = ax1.bar(clv_by_age['age_group'].astype(str), clv_by_age['avg_orders'],
                color=bar_colors_age, edgecolor='white', linewidth=0.8)
ax1.set_xlabel('Nhóm Tuổi', fontsize=12, fontweight='bold')
ax1.set_ylabel('Số Đơn Trung Bình / Khách Hàng', fontsize=12, fontweight='bold')
ax1.set_title('Giá Trị Vòng Đời Khách Hàng\nTheo Nhóm Tuổi', fontsize=14, fontweight='bold')
ax1.grid(axis='y', linestyle='--', alpha=0.4)

# Zoom in on y-axis to make differences visible
min_clv = clv_by_age['avg_orders'].min()
max_clv = clv_by_age['avg_orders'].max()
padding = (max_clv - min_clv) * 0.5
ax1.set_ylim(min_clv - padding, max_clv + padding)

for bar, row in zip(bars1, clv_by_age.itertuples()):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (padding * 0.1),
             f'{row.avg_orders:.2f}', ha='center', fontweight='bold', fontsize=11)
    ax1.text(bar.get_x() + bar.get_width()/2, min_clv - (padding * 0.5),
             f'({int(row.total_customers):,} KH)'.replace(',', '.'), ha='center', va='center',
             fontsize=10, color='white', fontweight='bold')

# Right: CLV by Acquisition Channel
clv_by_channel_sorted = clv_by_channel.sort_values('avg_orders', ascending=True)
max_clv_ch = clv_by_channel_sorted['avg_orders'].max()
bar_colors_ch = ['#e74c3c' if v == max_clv_ch else '#2ecc71' for v in clv_by_channel_sorted['avg_orders']]

bars2 = ax2.barh(clv_by_channel_sorted['channel_label'], clv_by_channel_sorted['avg_orders'],
                 color=bar_colors_ch, edgecolor='white', linewidth=0.8)
ax2.set_xlabel('Số Đơn Trung Bình / Khách Hàng', fontsize=12, fontweight='bold')
ax2.set_ylabel('')
ax2.set_title('Giá Trị Vòng Đời Khách Hàng\nTheo Kênh Marketing', fontsize=14, fontweight='bold')
ax2.grid(axis='x', linestyle='--', alpha=0.4)

# Zoom in on x-axis to make differences visible
min_clv_ch = clv_by_channel_sorted['avg_orders'].min()
max_clv_ch = clv_by_channel_sorted['avg_orders'].max()
padding_ch = (max_clv_ch - min_clv_ch) * 0.5
ax2.set_xlim(min_clv_ch - padding_ch, max_clv_ch + padding_ch)

for bar, (_, row) in zip(bars2, clv_by_channel_sorted.iterrows()):
    ax2.text(bar.get_width() + (padding_ch * 0.05), bar.get_y() + bar.get_height()/2,
             f'{row["avg_orders"]:.2f} ({int(row["total_customers"]):,} KH)'.replace(',', '.'),
             va='center', fontweight='bold', fontsize=10)

plt.tight_layout()
plt.savefig('Nop_bai/Images/11b_CLV_Age_Channel.png', dpi=300)
plt.close()
print("   -> Saved 11b_CLV_Age_Channel.png")

# ============================================================
# BONUS: Heatmap - Age x Channel cross-tabulation
# ============================================================
print("[Bonus] Age x Channel CLV Heatmap...")
clv_cross = orders_full.groupby(['customer_id', 'age_group', 'acquisition_channel']).size().reset_index(name='total_orders')
cross_agg = clv_cross.groupby(['age_group', 'acquisition_channel'])['total_orders'].mean().reset_index()
cross_agg['channel_label'] = cross_agg['acquisition_channel'].map(channel_vi)

cross_pivot = cross_agg.pivot(index='age_group', columns='channel_label', values='total_orders')
cross_pivot = cross_pivot.reindex(age_order)

fig, ax = plt.subplots(figsize=(12, 6))

# Center the colormap around the median to highlight differences better
median_val = cross_pivot.median().median()

sns.heatmap(cross_pivot, annot=True, fmt='.2f', 
            cmap='coolwarm', center=median_val, # Use coolwarm centered at median for strong contrast
            linewidths=1, linecolor='white',
            ax=ax, cbar_kws={'label': 'Số Đơn TB / Khách Hàng'})

ax.set_xlabel('Kênh Marketing', fontsize=12, fontweight='bold')
ax.set_ylabel('Nhóm Tuổi', fontsize=12, fontweight='bold')
ax.set_title('Ma trận nhiệt CLV: Nhóm Tuổi × Kênh Marketing', fontsize=14, fontweight='bold', pad=15)

# Ensure y-axis labels are horizontal
ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

plt.tight_layout()
plt.savefig('Nop_bai/Images/11c_CLV_Heatmap_Age_Channel.png', dpi=300)
plt.close()
print("   -> Saved 11c_CLV_Heatmap_Age_Channel.png")

print("\nAll demographic deep-dive visualizations completed!")
