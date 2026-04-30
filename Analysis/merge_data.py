import pandas as pd
import os

# Đường dẫn tới các file gốc
base_path = r"e:\project\datathon-2026-round-1"
products_path = os.path.join(base_path, "products.csv")
inventory_path = os.path.join(base_path, "inventory.csv")

# Đường dẫn file đầu ra trong thư mục Analysis
output_path = os.path.join(base_path, "Analysis", "merged_inventory_products.csv")

print("Đang đọc dữ liệu...")
products = pd.read_csv(products_path)
inventory = pd.read_csv(inventory_path)

print(f"Số dòng của products: {len(products)}")
print(f"Số dòng của inventory: {len(inventory)}")

print("Đang gộp dữ liệu (merge) theo product_id...")
# Sử dụng left join để giữ nguyên các dòng của inventory và lấy thêm thông tin từ products
merged_df = pd.merge(inventory, products, on='product_id', how='left')

print("Đang lưu file...")
merged_df.to_csv(output_path, index=False)

print(f"Hoàn tất! File đã được lưu tại:\n{output_path}")
print(f"Số dòng của file sau khi gộp: {len(merged_df)}")
