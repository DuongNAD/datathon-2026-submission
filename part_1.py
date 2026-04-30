import pandas as pd

# ==========================================
# 1. ĐỌC DỮ LIỆU TỔNG (CHỈ ĐỌC 1 LẦN)
# ==========================================
try:
    df_customers = pd.read_csv('customers.csv')
    df_orders = pd.read_csv('orders.csv')
    df_payments = pd.read_csv('payments.csv')
    df_geography = pd.read_csv('geography.csv')
    df_order_items = pd.read_csv('order_items.csv')
    df_returns = pd.read_csv('returns.csv')
    df_products = pd.read_csv('products.csv')
    # Chuyển đổi định dạng ngày tháng để dùng chung
    df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])

    # ==========================================
    # CÂU 6: Nhóm tuổi có đơn hàng trung bình cao nhất
    # ==========================================
    print("--- CÂU 6: PHÂN TÍCH THEO NHÓM TUỔI ---")
    
    # Đếm số đơn của mỗi khách hàng
    orders_per_customer = df_orders.groupby('customer_id').size().reset_index(name='order_count')
    
    # Join với bảng customers để lấy thông tin tuổi
    df_age_analysis = pd.merge(df_customers, orders_per_customer, on='customer_id', how='left')
    df_age_analysis['order_count'] = df_age_analysis['order_count'].fillna(0)
    
    # Lọc age_group khác null và tính toán
    df_age_final = df_age_analysis.dropna(subset=['age_group'])
    age_group_result = df_age_final.groupby('age_group').agg(
        total_orders=('order_count', 'sum'),
        total_customers=('customer_id', 'count')
    )
    age_group_result['avg_orders_per_customer'] = age_group_result['total_orders'] / age_group_result['total_customers']
    age_group_result = age_group_result.sort_values(by='avg_orders_per_customer', ascending=False)
    
    print(age_group_result)
    print(f"\n=> Nhóm tuổi có đơn hàng trung bình cao nhất: {age_group_result.index[0]}")
    print("-" * 50)


    # ==========================================
    # CÂU 7: Vùng (Region) có doanh thu cao nhất (Giai đoạn Train)
    # ==========================================
    print("\n--- CÂU 7: DOANH THU THEO VÙNG (TRAIN PERIOD) ---")
    
    # Lọc thời gian sales_train
    start_date, end_date = '2012-07-04', '2022-12-31'
    orders_train = df_orders[(df_orders['order_date'] >= start_date) & (df_orders['order_date'] <= end_date)]
    
    # Join Orders -> Payments -> Geography
    order_rev = pd.merge(orders_train[['order_id', 'zip']], df_payments[['order_id', 'payment_value']], on='order_id', how='inner')
    geo_rev = pd.merge(order_rev, df_geography[['zip', 'region']], on='zip', how='inner')
    
    # Tổng hợp theo vùng
    region_summary = geo_rev.groupby('region')['payment_value'].sum().reset_index()
    region_summary = region_summary.sort_values(by='payment_value', ascending=False)
    
    print(region_summary)
    if not region_summary.empty:
        top_region = region_summary.iloc[0]['region']
        print(f"\n=> Vùng có doanh thu cao nhất: {top_region}")
    print("-" * 50)


    # ==========================================
    # CÂU 8: Phương thức thanh toán bị hủy nhiều nhất
    # ==========================================
    print("\n--- CÂU 8: PHƯƠNG THỨC THANH TOÁN CỦA ĐƠN HÀNG BỊ HỦY ---")
    
    # Lọc đơn hàng cancelled
    cancelled_orders = df_orders[df_orders['order_status'] == 'cancelled']
    payment_counts = cancelled_orders['payment_method'].value_counts()
    
    print(payment_counts)
    if not payment_counts.empty:
        print(f"\n=> Phương thức thanh toán bị hủy nhiều nhất: {payment_counts.idxmax()} ({payment_counts.max()} đơn)")

except FileNotFoundError as e:
    print(f"Lỗi: Không tìm thấy file. Hãy kiểm tra lại đường dẫn: {e}")
except Exception as e:
    print(f"Lỗi hệ thống: {e}")

# ==========================================
# CÂU 9: Phương thức thanh toán bị hủy nhiều nhất
# ==========================================
print("\n--- CÂU 9: PHƯƠNG THỨC THANH TOÁN CỦA ĐƠN HÀNG BỊ HỦY ---")
# 2. Tính số bản ghi trả hàng cho mỗi product_id (Mẫu số: Số dòng trong returns)
# Lưu ý: Đề bài bảo "số bản ghi trong returns", nên ta đếm số dòng
return_counts = df_returns.groupby('product_id').size().reset_index(name='return_records')

# 3. Tính số dòng bán ra cho mỗi product_id (Tử số: Số dòng trong order_items)
sales_counts = df_order_items.groupby('product_id').size().reset_index(name='sales_records')

# 4. Join với bảng products để lấy thông tin Size
# Ta join cả 2 thông tin trên vào bảng products
df_size_analysis = pd.merge(df_products[['product_id', 'size']], return_counts, on='product_id', how='left')
df_size_analysis = pd.merge(df_size_analysis, sales_counts, on='product_id', how='left')

# Điền 0 cho những sản phẩm không có lượt bán hoặc không có lượt trả
df_size_analysis[['return_records', 'sales_records']] = df_size_analysis[['return_records', 'sales_records']].fillna(0)

# 5. Gom nhóm theo Size để tính tỷ lệ tổng
# Công thức: Tổng số bản ghi returns trong nhóm / Tổng số dòng order_items trong nhóm
size_report = df_size_analysis.groupby('size').agg(
    total_returns=('return_records', 'sum'),
    total_sales=('sales_records', 'sum')
)

# Tránh chia cho 0 nếu có size nào đó không bán được dòng nào
size_report['return_rate'] = size_report['total_returns'] / size_report['total_sales']

# 6. Lọc chỉ lấy 4 kích thước yêu cầu và sắp xếp
target_sizes = ['S', 'M', 'L', 'XL']
size_report = size_report.loc[size_report.index.isin(target_sizes)].sort_values(by='return_rate', ascending=False)

print(size_report)
if not size_report.empty:
    print(f"\n=> Kích thước có tỷ lệ trả hàng cao nhất là: {size_report.index[0]}")

# ==========================================
# CÂU 10: Kế hoạch trả góp có giá trị trung bình cao nhất
# ==========================================
print("\n--- Câu 10: PHÂN TÍCH GIÁ TRỊ THANH TOÁN THEO KỲ TRẢ GÓP ---")

# 2. Nhóm theo số kỳ trả góp (installments) và tính trung bình payment_value
installment_analysis = df_payments.groupby('installments')['payment_value'].mean().reset_index()

# 3. Đặt lại tên cột cho rõ ràng
installment_analysis.columns = ['installments', 'avg_payment_value']

# 4. Sắp xếp để tìm kế hoạch có giá trị trung bình cao nhất
installment_analysis = installment_analysis.sort_values(by='avg_payment_value', ascending=False)

print(installment_analysis)

if not installment_analysis.empty:
    top_plan = installment_analysis.iloc[0]['installments']
    top_avg_value = installment_analysis.iloc[0]['avg_payment_value']
    print(f"\n=> Kế hoạch trả góp có giá trị trung bình mỗi đơn cao nhất là: {top_plan} kỳ (Trung bình: {top_avg_value:,.2f})")