import pandas as pd

print("Analyzing Peak Months (April, May, June)...")

orders = pd.read_csv('orders.csv')
order_items = pd.read_csv('order_items.csv')
products = pd.read_csv('products.csv')
promotions = pd.read_csv('promotions.csv')

orders['order_date'] = pd.to_datetime(orders['order_date'])
orders['month'] = orders['order_date'].dt.month

df = order_items.merge(orders[['order_id', 'month']], on='order_id', how='left')
df = df.merge(products[['product_id', 'category']], on='product_id', how='left')
df = df.merge(promotions[['promo_id', 'promo_name']], on='promo_id', how='left')

df['Revenue'] = df['unit_price'] * df['quantity']

# Filter for months 4, 5, 6
df_peak = df[df['month'].isin([4, 5, 6])].copy()

# Analyze by category
cat_sales = df_peak.groupby('category')['Revenue'].sum().sort_values(ascending=False)
print("\n--- Revenue by Category in Q2 (Months 4-6) ---")
print(cat_sales)

# Analyze by promotion
promo_sales = df_peak.groupby('promo_name')['Revenue'].sum().sort_values(ascending=False)
print("\n--- Revenue by Promotion in Q2 (Months 4-6) ---")
print(promo_sales.head(10))

# Compare with other months
df_other = df[~df['month'].isin([4, 5, 6])].copy()
cat_sales_other = df_other.groupby('category')['Revenue'].sum()
print("\n--- Average Monthly Revenue by Category: Q2 vs Others ---")
q2_avg = cat_sales / 3
other_avg = cat_sales_other / 9
comp = pd.DataFrame({'Q2_Avg_Monthly': q2_avg, 'Other_Avg_Monthly': other_avg})
comp['Growth'] = (comp['Q2_Avg_Monthly'] / comp['Other_Avg_Monthly'] - 1) * 100
print(comp.sort_values('Growth', ascending=False))
