import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

print("Generating Revenue and Profit by Year...")

# Load data
orders = pd.read_csv('orders.csv')
order_items = pd.read_csv('order_items.csv')
products = pd.read_csv('products.csv')

# Extract year
orders['order_date'] = pd.to_datetime(orders['order_date'])
orders['year'] = orders['order_date'].dt.year

# Merge
df = order_items.merge(orders[['order_id', 'year']], on='order_id', how='left')
df = df.merge(products[['product_id', 'cogs']], on='product_id', how='left')

# Calculate Revenue, COGS, Profit
df['Revenue'] = df['unit_price'] * df['quantity']
df['COGS_total'] = df['cogs'] * df['quantity']
df['Discount'] = df['discount_amount'].fillna(0)
df['Profit'] = df['Revenue'] - df['COGS_total'] - df['Discount']

# Group by Year
yearly = df.groupby('year').agg(
    Total_Revenue=('Revenue', 'sum'),
    Total_Profit=('Profit', 'sum')
).reset_index()

# Sort by year just in case
yearly = yearly.sort_values('year')

# Plot Dual Axis Chart
fig, ax1 = plt.subplots(figsize=(10, 6))

# Bar chart for Revenue
sns.barplot(data=yearly, x='year', y='Total_Revenue', color='royalblue', alpha=0.7, ax=ax1, label='Total Revenue')
ax1.set_ylabel('Total Revenue (VNĐ)', color='royalblue', fontsize=12, fontweight='bold')
ax1.tick_params(axis='y', labelcolor='royalblue')
ax1.set_xlabel('Year', fontsize=12, fontweight='bold')

# Create a second y-axis for Profit
ax2 = ax1.twinx()
sns.lineplot(data=yearly, x=range(len(yearly)), y='Total_Profit', color='darkred', marker='o', linewidth=3, markersize=8, ax=ax2, label='Total Profit')
ax2.set_ylabel('Total Profit (VNĐ)', color='darkred', fontsize=12, fontweight='bold')
ax2.tick_params(axis='y', labelcolor='darkred')

# Title
plt.title('Doanh thu và Lợi nhuận theo năm (2013 - 2022)', fontsize=15, fontweight='bold')

# Legends
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

plt.tight_layout()
plt.savefig('./Nop_bai/Images/10_Revenue_Profit_Yearly.png', dpi=300)
plt.close()

print(yearly)
print("Saved to ./Nop_bai/Images/10_Revenue_Profit_Yearly.png")
