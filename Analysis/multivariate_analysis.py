import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. Promotion vs Profit Margin
print("--- Promotion vs Profit Margin ---")
order_items = pd.read_csv('order_items.csv')
products = pd.read_csv('products.csv')
promotions = pd.read_csv('promotions.csv')

# Merge
df = order_items.merge(products, on='product_id', how='left')
df = df.merge(promotions, on='promo_id', how='left')

# Calculate Revenue, COGS, Discount, Profit
df['Revenue'] = df['unit_price'] * df['quantity']
df['COGS_total'] = df['cogs'] * df['quantity']
df['Discount'] = df['discount_amount']
df['Profit'] = df['Revenue'] - df['COGS_total'] - df['Discount']

# Group by promotion (strip year for cleaner chart)
df['promo_base_name'] = df['promo_name'].str.replace(r'\s\d{4}$', '', regex=True)
promo_perf = df[df['promo_base_name'].notna()].groupby('promo_base_name').agg(
    Total_Revenue=('Revenue', 'sum'),
    Total_Profit=('Profit', 'sum')
).reset_index()

promo_perf['Profit_Margin'] = promo_perf['Total_Profit'] / promo_perf['Total_Revenue']
promo_perf = promo_perf.sort_values('Profit_Margin', ascending=False)
print(promo_perf)

# Lưu file CSV chứng minh
promo_perf.to_csv('./Nop_bai/Chung_minh_Loi_nhuan_Khuyen_mai.csv', index=False)

# Plot
plt.figure(figsize=(10, 6))
sns.barplot(data=promo_perf, x='Profit_Margin', y='promo_base_name', 
            hue='promo_base_name', palette=['red' if x < 0 else 'green' for x in promo_perf['Profit_Margin']], legend=False)
plt.title('TƯƠNG QUAN GIỮA CHIẾN DỊCH KHUYẾN MÃI VÀ BIÊN LỢI NHUẬN', fontsize=14, fontweight='bold')
plt.xlabel('Biên lợi nhuận (%)')
plt.ylabel('')
plt.axvline(0, color='black', linewidth=1)

import matplotlib.ticker as mtick
plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(1.0))

# Add annotations
for p in plt.gca().patches:
    width = p.get_width()
    if width != 0:
        offset = 0.01 if width > 0 else -0.06
        plt.text(width + offset, p.get_y() + p.get_height()/2., 
                 f'{width*100:.1f}%', va="center", fontsize=10, fontweight='bold')

# Adjust xlim to fit labels
plt.xlim(-0.75, 0.15)

plt.tight_layout()
plt.savefig('./Nop_bai/Images/9a_Promotion_Profit_Margin.png', dpi=300)
plt.close()

# 2. Inventory Health vs Sales Velocity
print("\n--- Inventory Health vs Sales Velocity ---")
inventory = pd.read_csv('inventory.csv')
inv_agg = inventory.groupby(['product_name', 'category']).agg(
    Avg_Stock_On_Hand=('stock_on_hand', 'mean'),
    Total_Units_Sold=('units_sold', 'sum')
).reset_index()

print("High stock, low sales (Inventory Crisis):")
crisis = inv_agg[(inv_agg['Avg_Stock_On_Hand'] > inv_agg['Avg_Stock_On_Hand'].median()) & 
                 (inv_agg['Total_Units_Sold'] < inv_agg['Total_Units_Sold'].median())]
print(crisis.head())

plt.figure(figsize=(10, 6))
sns.scatterplot(data=inv_agg, x='Total_Units_Sold', y='Avg_Stock_On_Hand', hue='category', s=100, alpha=0.7)
plt.title('SỨC KHỎE TỒN KHO VS TỐC ĐỘ BÁN', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Tốc độ bán (Tổng số lượng đã bán)')
plt.ylabel('Tồn kho trung bình (Đơn vị)')
plt.legend(title='Danh mục')

plt.tight_layout()
plt.savefig('./Nop_bai/Images/9b_Inventory_Sales_Velocity.png', dpi=300)
plt.close()
