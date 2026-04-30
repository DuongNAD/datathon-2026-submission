import os
import shutil
import glob

source_dir = '.'
target_dir = 'For_NotebookLM'
split_dir = 'Split_Data'

os.makedirs(target_dir, exist_ok=True)

# Các file gốc đã bị chia nhỏ (không copy)
split_parents = ['orders.csv', 'order_items.csv', 'payments.csv', 'shipments.csv']

print("Bắt đầu gom file...")

# 1. Copy các file không bị chia nhỏ (loại trừ các file cha)
for file_path in glob.glob('*.*'):
    file_name = os.path.basename(file_path)
    # Bỏ qua thư mục (nếu glob *.* match)
    if os.path.isdir(file_path):
        continue
    # Bỏ qua file code và .ipynb nếu muốn, nhưng ở đây cứ copy hết trừ .py
    if file_name.endswith('.py') or file_name == target_dir or file_name in split_parents:
        continue
        
    print(f"Đang copy file nguyên bản: {file_name}")
    shutil.copy2(file_path, os.path.join(target_dir, file_name))
        
# 2. Copy tất cả các file đã chia nhỏ từ trong thư mục Split_Data
if os.path.exists(split_dir):
    for root, dirs, files in os.walk(split_dir):
        for file in files:
            if file.endswith('.csv'):
                print(f"Đang copy file đã cắt: {file}")
                shutil.copy2(os.path.join(root, file), os.path.join(target_dir, file))

print(f"\nHoàn tất! Tất cả các file đã được gom vào thư mục: {target_dir}")
