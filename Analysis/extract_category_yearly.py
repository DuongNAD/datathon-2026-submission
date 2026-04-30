import pandas as pd
import os

base_path = r"e:\project\datathon-2026-round-1\Analysis"
input_path = os.path.join(base_path, "merged_inventory_products.csv")

print("Đang đọc dữ liệu đã merge...")
df = pd.read_csv(input_path)

# Merge tạo ra category_x (từ inventory) và category_y (từ products), ta gộp lại thành category
if 'category_x' in df.columns:
    df['category'] = df['category_x']
elif 'category_y' in df.columns:
    df['category'] = df['category_y']

# Tính toán các chỉ số cho từng category theo từng năm
print("Đang tổng hợp thông tin category theo từng năm...")
yearly_stats = df.groupby(['year', 'category']).agg({
    'units_sold': 'sum',
    'units_received': 'sum',
    'stock_on_hand': 'sum'
}).reset_index()

yearly_stats = yearly_stats.rename(columns={
    'year': 'Năm',
    'category': 'Danh Mục',
    'units_sold': 'Bán Ra (Tổng)', 
    'units_received': 'Nhập Kho (Tổng)', 
    'stock_on_hand': 'Tồn Kho (Tổng)'
})

# Lưu 1 file tổng chứa toàn bộ các năm
full_output_path = os.path.join(base_path, "category_yearly_full.csv")
yearly_stats.to_csv(full_output_path, index=False, encoding='utf-8-sig')
print(f"Đã lưu bản đầy đủ tại: {full_output_path}")

# Tạo thư mục con để lưu riêng từng năm cho dễ theo dõi
split_dir = os.path.join(base_path, "Category_By_Year")
os.makedirs(split_dir, exist_ok=True)

years = yearly_stats['Năm'].unique()
for y in sorted(years):
    df_year = yearly_stats[yearly_stats['Năm'] == y]
    year_output_path = os.path.join(split_dir, f"category_info_{int(y)}.csv")
    df_year.to_csv(year_output_path, index=False, encoding='utf-8-sig')

print(f"Đã chia tách và lưu thông tin từng năm riêng lẻ vào thư mục: {split_dir}")
