import pandas as pd
import numpy as np

print("Analyzing August Anomaly (Odd vs Even Years)...")

orders = pd.read_csv('orders.csv')
order_items = pd.read_csv('order_items.csv')
products = pd.read_csv('products.csv')

# Merge
orders['order_date'] = pd.to_datetime(orders['order_date'])
orders['year'] = orders['order_date'].dt.year
orders['month'] = orders['order_date'].dt.month

df = order_items.merge(orders[['order_id', 'year', 'month']], on='order_id', how='left')
df = df.merge(products[['product_id', 'cogs']], on='product_id', how='left')

# Filter for August
df_aug = df[df['month'] == 8].copy()

# Add odd/even flag
df_aug['year_type'] = np.where(df_aug['year'] % 2 != 0, 'Odd Year (2013, 2015...)', 'Even Year (2014, 2016...)')

# Calculate financial metrics
df_aug['Revenue'] = df_aug['unit_price'] * df_aug['quantity']
df_aug['COGS_total'] = df_aug['cogs'] * df_aug['quantity']
df_aug['Discount'] = df_aug['discount_amount'].fillna(0)
df_aug['Profit'] = df_aug['Revenue'] - df_aug['COGS_total'] - df_aug['Discount']

# Aggregate by year type
aug_summary = df_aug.groupby('year_type').agg(
    Total_Orders=('order_id', 'nunique'),
    Total_Units=('quantity', 'sum'),
    Total_Revenue=('Revenue', 'sum'),
    Total_Discount=('Discount', 'sum'),
    Total_Profit=('Profit', 'sum')
).reset_index()

aug_summary['Profit_Margin'] = aug_summary['Total_Profit'] / aug_summary['Total_Revenue']
aug_summary['Discount_Rate'] = aug_summary['Total_Discount'] / (aug_summary['Total_Revenue'] + aug_summary['Total_Discount'])

print("\n--- August Summary by Year Type ---")
print(aug_summary.to_string())

# Let's check promotions in August
promotions = pd.read_csv('promotions.csv')
promotions['start_date'] = pd.to_datetime(promotions['start_date'])
promotions['end_date'] = pd.to_datetime(promotions['end_date'])

# Find promotions active in August
promo_aug = promotions[
    ((promotions['start_date'].dt.month <= 8) & (promotions['end_date'].dt.month >= 8))
].copy()
promo_aug['year'] = promo_aug['start_date'].dt.year
promo_aug['year_type'] = np.where(promo_aug['year'] % 2 != 0, 'Odd', 'Even')

print("\n--- Promotions Active in August (Odd vs Even) ---")
print(promo_aug.groupby(['year_type', 'promo_type']).size().reset_index(name='Count'))
print("\nDiscount values of these promotions:")
print(promo_aug.groupby(['year_type', 'promo_type'])['discount_value'].mean().reset_index(name='Avg_Discount_Value'))
