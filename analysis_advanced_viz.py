import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import os

plt.rcParams['font.size'] = 12
os.makedirs('Nop_bai/Images', exist_ok=True)

# ============================================================
# Load data
# ============================================================
orders = pd.read_csv('orders.csv')
orders['order_date'] = pd.to_datetime(orders['order_date'])
returns = pd.read_csv('returns.csv')
sales = pd.read_csv('train_model/dataset/sales_train.csv')
sales['Date'] = pd.to_datetime(sales['Date'])

# ============================================================
# 1. COHORT ANALYSIS HEATMAP - Retention Rate
# ============================================================
print("[1/3] Building Cohort Heatmap...")

# Determine each customer's first order month (cohort)
orders['order_month'] = orders['order_date'].dt.to_period('M')
cohort_df = orders.groupby('customer_id')['order_month'].min().reset_index()
cohort_df.columns = ['customer_id', 'cohort_month']
orders = orders.merge(cohort_df, on='customer_id')

# Aggregate by YEAR instead of month for readability
orders['cohort_year'] = orders['cohort_month'].dt.year
orders['order_year'] = orders['order_date'].dt.year
orders['year_offset'] = orders['order_year'] - orders['cohort_year']

yearly_cohort = orders.groupby(['cohort_year', 'year_offset'])['customer_id'].nunique().reset_index()
yearly_cohort.columns = ['cohort_year', 'year_offset', 'num_customers']
yearly_pivot = yearly_cohort.pivot(index='cohort_year', columns='year_offset', values='num_customers')
yearly_sizes = yearly_pivot[0]
yearly_retention = yearly_pivot.divide(yearly_sizes, axis=0)

# Only keep offsets 0-5 for clarity
yearly_retention = yearly_retention.loc[:, yearly_retention.columns <= 5]

# Mask future years (triangular heatmap)
max_year = orders['order_year'].max()
for col in yearly_retention.columns:
    yearly_retention.loc[yearly_retention.index + col > max_year, col] = np.nan

fig, ax = plt.subplots(figsize=(12, 7))
sns.heatmap(
    yearly_retention,
    annot=True, fmt='.1%',
    cmap='YlGnBu', # Changed color map for better contrast
    linewidths=1, linecolor='white',
    vmin=0, vmax=1,
    ax=ax,
    cbar_kws={'label': 'Tỷ lệ Giữ chân', 'shrink': 0.8}
)
ax.set_xlabel('Số Năm Sau Lần Mua Đầu Tiên', fontsize=13, fontweight='bold')
ax.set_ylabel('Năm Gia Nhập', fontsize=13, fontweight='bold')
ax.set_title('Ma trận nhiệt Cohort: Tỷ Lệ Giữ Chân Khách Hàng Theo Năm', fontsize=15, fontweight='bold', pad=15)

# Fix y-axis labels to be horizontal
ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

plt.tight_layout()
plt.savefig('Nop_bai/Images/10a_Cohort_Heatmap.png', dpi=300)
plt.close()
print("   -> Saved 10a_Cohort_Heatmap.png")

# ============================================================
# 2. PARETO CHART (80/20 Rule) - Top Products by Revenue
# ============================================================
print("[2/3] Building Pareto Chart...")

# Pareto by Customer: which 20% of customers drive 80% of orders?
customer_orders = orders.groupby('customer_id').size().reset_index(name='order_count')
customer_orders = customer_orders.sort_values('order_count', ascending=False).reset_index(drop=True)
customer_orders['cumulative_orders'] = customer_orders['order_count'].cumsum()
total_orders = customer_orders['order_count'].sum()
customer_orders['cumulative_pct'] = customer_orders['cumulative_orders'] / total_orders * 100
customer_orders['customer_pct'] = (customer_orders.index + 1) / len(customer_orders) * 100

fig, ax1 = plt.subplots(figsize=(12, 7))

# Bar chart - individual contribution binned nicely
n_bins = 20 # 5% increments
bin_size = len(customer_orders) // n_bins
binned = []
for i in range(n_bins):
    start = i * bin_size
    end = start + bin_size if i < n_bins - 1 else len(customer_orders)
    chunk = customer_orders.iloc[start:end]
    binned.append({
        'bin_label': f'Top {(i+1)*5}%',
        'order_count': chunk['order_count'].sum(),
        'cumulative_pct': chunk['cumulative_pct'].iloc[-1],
        'customer_pct': chunk['customer_pct'].iloc[-1]
    })
binned_df = pd.DataFrame(binned)

colors = ['#e74c3c' if row['cumulative_pct'] <= 80 else '#3498db' for _, row in binned_df.iterrows()]
ax1.bar(binned_df['bin_label'], binned_df['order_count'], color=colors, alpha=0.85, width=0.8)
ax1.set_ylabel('Số lượng Đơn hàng', fontsize=12, fontweight='bold', color='#2c3e50')
ax1.set_xlabel('Tệp Khách Hàng', fontsize=12, fontweight='bold')

# Rotate x labels nicely
ax1.set_xticklabels(binned_df['bin_label'], rotation=45, ha='right')

# Tăng khoảng trống phía trên để tránh đè legend
ax1.set_ylim(0, binned_df['order_count'].max() * 1.25)

# Line chart - cumulative %
ax2 = ax1.twinx()
ax2.plot(binned_df['bin_label'], binned_df['cumulative_pct'], color='#e67e22', linewidth=3, marker='o', markersize=6, label='Tích lũy (%)')
ax2.set_ylabel('Tỷ lệ Tích lũy Đơn hàng (%)', fontsize=12, fontweight='bold', color='#e67e22')
ax2.set_ylim(0, 105)

# 80% threshold line
ax2.axhline(y=80, color='#e74c3c', linestyle='--', linewidth=2, alpha=0.7)
# Find where cumulative crosses 80%
cross_idx = binned_df[binned_df['cumulative_pct'] >= 80].index[0]
cross_pct = binned_df.iloc[cross_idx]['customer_pct']
ax2.annotate(
    f'80% đơn hàng đến từ\nchỉ ~{cross_pct:.0f}% khách hàng',
    xy=(cross_idx, 80), xytext=(cross_idx + 2, 60),
    fontsize=12, fontweight='bold', color='#e74c3c',
    arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=2),
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffeaa7', edgecolor='#e74c3c', alpha=0.9)
)

ax1.set_title('Phân tích Pareto: Phân Bố Đóng Góp Khách Hàng', fontsize=15, fontweight='bold', pad=15)
ax1.grid(axis='y', linestyle='--', alpha=0.4)
fig.legend(['Tích lũy (%)'], loc='upper center', bbox_to_anchor=(0.5, 0.95), ncol=2, fontsize=11, frameon=True)
plt.tight_layout()
plt.savefig('Nop_bai/Images/10b_Pareto_Chart.png', dpi=300)
plt.close()
print("   -> Saved 10b_Pareto_Chart.png")

# ============================================================
# 3. SANKEY DIAGRAM - Customer Journey Flow
# ============================================================
print("[3/3] Building Sankey Diagram...")

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

if HAS_PLOTLY:
    # Build flow: Traffic Source -> Order Status -> (if returned) Return Reason
    # Stage 1: Traffic Source -> Order Status
    flow1 = orders.groupby(['order_source', 'order_status']).size().reset_index(name='count')

    # Stage 2: Returned orders -> Return Reason
    returned_orders = orders[orders['order_status'] == 'returned'][['order_id', 'order_source']]
    returned_with_reason = returned_orders.merge(returns[['order_id', 'return_reason']].drop_duplicates(), on='order_id', how='left')
    flow2 = returned_with_reason.groupby(['order_status_label', 'return_reason']).size().reset_index(name='count') if False else None

    # Simplify: just do Traffic Source -> Final Outcome (delivered / cancelled / returned / processing)
    orders_copy = orders.copy()
    orders_copy['final_status'] = orders_copy['order_status'].map({
        'delivered': 'Giao thành công',
        'cancelled': 'Hủy đơn',
        'returned': 'Trả hàng',
        'shipped': 'Đang vận chuyển',
        'paid': 'Đã thanh toán',
        'created': 'Mới tạo'
    })

    source_mapping = {
        'organic_search': 'Organic Search',
        'paid_search': 'Paid Search',
        'social_media': 'Social Media',
        'email_campaign': 'Email Campaign',
        'referral': 'Referral',
        'direct': 'Direct'
    }
    orders_copy['source_label'] = orders_copy['order_source'].map(source_mapping)

    flow_data = orders_copy.groupby(['source_label', 'final_status']).size().reset_index(name='count')

    # For returned orders, add return reason as 3rd level
    returned_ids = orders_copy[orders_copy['order_status'] == 'returned']['order_id']
    ret_detail = returns[returns['order_id'].isin(returned_ids)].copy()
    reason_mapping = {
        'wrong_size': 'Sai kích cỡ',
        'defective': 'Lỗi sản phẩm',
        'not_as_described': 'Không đúng mô tả',
        'changed_mind': 'Đổi ý',
        'late_delivery': 'Giao chậm'
    }
    ret_detail['reason_label'] = ret_detail['return_reason'].map(reason_mapping)
    flow_return = ret_detail.groupby('reason_label').size().reset_index(name='count')

    # Build Sankey nodes and links
    sources_list = list(flow_data['source_label'].unique())
    statuses_list = list(flow_data['final_status'].unique())
    reasons_list = list(flow_return['reason_label'].unique())
    all_nodes = sources_list + statuses_list + reasons_list

    node_colors_map = {
        'Organic Search': '#27ae60', 'Paid Search': '#2980b9', 'Social Media': '#8e44ad',
        'Email Campaign': '#e67e22', 'Referral': '#16a085', 'Direct': '#7f8c8d',
        'Giao thành công': '#2ecc71', 'Hủy đơn': '#e74c3c', 'Trả hàng': '#f39c12',
        'Đang vận chuyển': '#3498db', 'Đã thanh toán': '#1abc9c', 'Mới tạo': '#95a5a6',
        'Sai kích cỡ': '#e74c3c', 'Lỗi sản phẩm': '#c0392b',
        'Không đúng mô tả': '#d35400', 'Đổi ý': '#f1c40f', 'Giao chậm': '#e67e22'
    }
    node_colors = [node_colors_map.get(n, '#bdc3c7') for n in all_nodes]

    links_source = []
    links_target = []
    links_value = []
    links_color = []

    for _, row in flow_data.iterrows():
        links_source.append(all_nodes.index(row['source_label']))
        links_target.append(all_nodes.index(row['final_status']))
        links_value.append(row['count'])
        base_color = node_colors_map.get(row['source_label'], '#bdc3c7')
        # Make link color semi-transparent
        r, g, b = mcolors.to_rgb(base_color)
        links_color.append(f'rgba({int(r*255)},{int(g*255)},{int(b*255)},0.35)')

    # Links from "Trả hàng" to return reasons
    tra_hang_idx = all_nodes.index('Trả hàng')
    for _, row in flow_return.iterrows():
        links_source.append(tra_hang_idx)
        links_target.append(all_nodes.index(row['reason_label']))
        links_value.append(row['count'])
        links_color.append('rgba(243,156,18,0.35)')

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=20, thickness=25,
            line=dict(color='white', width=1),
            label=all_nodes,
            color=node_colors
        ),
        link=dict(
            source=links_source,
            target=links_target,
            value=links_value,
            color=links_color
        )
    ))
    fig.update_layout(
        title_text='Biểu đồ Sankey: Hành Trình Khách Hàng (Nguồn Truy Cập → Trạng Thái Đơn → Lý Do Trả Hàng)',
        title_font_size=16,
        font_size=12,
        width=1200, height=700
    )
    fig.write_image('Nop_bai/Images/10c_Sankey_Diagram.png', scale=2)
    print("   -> Saved 10c_Sankey_Diagram.png")

else:
    # Fallback: matplotlib-based flow visualization
    print("   Plotly not found. Building matplotlib Sankey fallback...")

    flow_data = orders.groupby(['order_source', 'order_status']).size().reset_index(name='count')

    source_labels = {
        'organic_search': 'Organic Search', 'paid_search': 'Paid Search',
        'social_media': 'Social Media', 'email_campaign': 'Email',
        'referral': 'Referral', 'direct': 'Direct'
    }
    status_labels = {
        'delivered': 'Giao thành công', 'cancelled': 'Hủy đơn',
        'returned': 'Trả hàng', 'shipped': 'Đang vận chuyển',
        'paid': 'Đã thanh toán', 'created': 'Mới tạo'
    }
    flow_data['source_label'] = flow_data['order_source'].map(source_labels)
    flow_data['status_label'] = flow_data['order_status'].map(status_labels)

    # Aggregate top flows
    flow_data = flow_data.sort_values('count', ascending=False)

    # Group by source for stacked horizontal bar
    source_totals = flow_data.groupby('source_label')['count'].sum().sort_values(ascending=True)
    status_names = list(flow_data['status_label'].unique())
    status_colors = {
        'Giao thành công': '#2ecc71', 'Hủy đơn': '#e74c3c',
        'Trả hàng': '#f39c12', 'Đang vận chuyển': '#3498db',
        'Đã thanh toán': '#1abc9c', 'Mới tạo': '#95a5a6'
    }

    fig, ax = plt.subplots(figsize=(14, 7))
    left_positions = {s: 0 for s in source_totals.index}

    for status in ['Giao thành công', 'Hủy đơn', 'Trả hàng', 'Đang vận chuyển', 'Đã thanh toán', 'Mới tạo']:
        widths = []
        for source in source_totals.index:
            val = flow_data[(flow_data['source_label'] == source) & (flow_data['status_label'] == status)]['count'].sum()
            widths.append(val)
        lefts = [left_positions[s] for s in source_totals.index]
        bars = ax.barh(list(source_totals.index), widths, left=lefts,
                       color=status_colors.get(status, '#bdc3c7'), label=status, edgecolor='white', linewidth=0.5)
        for s, w in zip(source_totals.index, widths):
            left_positions[s] += w

    ax.set_xlabel('Số lượng Đơn hàng', fontsize=12, fontweight='bold')
    ax.set_ylabel('Nguồn Truy cập', fontsize=12, fontweight='bold')
    ax.set_title('Luồng Hành Trình Khách Hàng: Nguồn Truy Cập → Trạng Thái Đơn Hàng', fontsize=15, fontweight='bold', pad=15)
    ax.legend(title='Trạng thái Đơn hàng', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=10)
    ax.grid(axis='x', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig('Nop_bai/Images/10c_Sankey_Diagram.png', dpi=300)
    plt.close()
    print("   -> Saved 10c_Sankey_Diagram.png (matplotlib fallback)")

print("\nAll 3 advanced visualizations completed!")
