import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# Load Data
print("Loading data...")
orders = pd.read_csv(r"e:\project\datathon-2026-round-1\orders.csv", parse_dates=['order_date'])
order_items = pd.read_csv(r"e:\project\datathon-2026-round-1\order_items.csv")
products = pd.read_csv(r"e:\project\datathon-2026-round-1\products.csv")

# Merge
print("Merging...")
# We need revenue. order_items has quantity, discount_amount. products has price.
merged = order_items.merge(products[['product_id', 'category', 'price']], on='product_id')
merged['revenue'] = (merged['quantity'] * merged['price']) - merged['discount_amount'].fillna(0)
merged = merged.merge(orders[['order_id', 'order_date']], on='order_id')

# Extract Month
merged['month'] = merged['order_date'].dt.month
merged['is_q2'] = merged['month'].isin([4, 5, 6])

# Group by Category and Q2 vs Other
grouped = merged.groupby(['category', 'is_q2'])['revenue'].sum().reset_index()

# Calculate Average Monthly Revenue
# Q2 has 3 months, Other has 9 months
grouped['avg_monthly_rev'] = grouped.apply(lambda row: row['revenue'] / 3 if row['is_q2'] else row['revenue'] / 9, axis=1)

# Pivot to calculate growth
pivot = grouped.pivot(index='category', columns='is_q2', values='avg_monthly_rev').reset_index()
pivot.columns = ['category', 'other_months', 'q2']
pivot['growth_pct'] = ((pivot['q2'] - pivot['other_months']) / pivot['other_months']) * 100

# Sort by growth
pivot = pivot.sort_values(by='growth_pct', ascending=False)

# Visualizing
print("Plotting...")
sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))

# Highlight Streetwear, GenZ, and Casual
colors = ['#E74C3C' if cat in ['Streetwear', 'GenZ', 'Casual'] else '#BDC3C7' for cat in pivot['category']]

ax = sns.barplot(x='category', y='growth_pct', data=pivot, palette=colors)
plt.title("TỐC ĐỘ TĂNG TRƯỞNG DOANH THU QUÝ 2 THEO DANH MỤC\n(So với trung bình các tháng khác)", fontsize=16, fontweight='bold', pad=20)
plt.ylabel("Mức tăng trưởng (%)", fontsize=12)
plt.xlabel("")
plt.xticks(rotation=45)

# Add value labels
for p in ax.patches:
    height = p.get_height()
    va = 'bottom' if height > 0 else 'top'
    offset = 2 if height > 0 else -4
    plt.text(p.get_x() + p.get_width()/2., height + offset, f'{height:+.1f}%', ha='center', va=va, fontsize=12, fontweight='bold', color='#333333')

# Expand ylim a bit for the text
plt.ylim(min(pivot['growth_pct'].min() - 10, 0), pivot['growth_pct'].max() + 20)

# Add a horizontal line at 0
plt.axhline(0, color='black', linewidth=1)

plt.tight_layout()

# Save
out_dir = r"e:\project\datathon-2026-round-1\Nop_bai\Images"
out_path = os.path.join(out_dir, "4c_Category_Growth_Q2_Comprehensive.png")
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Chart saved to {out_path}")
