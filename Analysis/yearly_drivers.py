import pandas as pd

orders = pd.read_csv('orders.csv')
order_items = pd.read_csv('order_items.csv')

orders['order_date'] = pd.to_datetime(orders['order_date'])
orders['year'] = orders['order_date'].dt.year

df = order_items.merge(orders[['order_id', 'year']], on='order_id', how='left')
df['Revenue'] = df['unit_price'] * df['quantity']

# Aggregate by year
yearly = df.groupby('year').agg(
    Total_Revenue=('Revenue', 'sum'),
    Total_Orders=('order_id', 'nunique'),
    Units_Sold=('quantity', 'sum')
).reset_index()

yearly['AOV'] = yearly['Total_Revenue'] / yearly['Total_Orders']
print(yearly.to_string())

# Also check category shifts
products = pd.read_csv('products.csv')
df = df.merge(products[['product_id', 'category']], on='product_id', how='left')
cat_yearly = df.groupby(['year', 'category'])['Revenue'].sum().unstack()
print("\nCategory Revenue by Year:")
print(cat_yearly.to_string())
