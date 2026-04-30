import pandas as pd
import os
import glob

# Thư mục hiện tại (nơi chứa các file csv)
input_dir = '.'
# Thư mục output
output_dir = 'Split_Data'
os.makedirs(output_dir, exist_ok=True)

chunk_size = 100000  # Giới hạn mỗi file sẽ chứa 100.000 dòng

# Lọc ra những file dung lượng từ 15MB trở lên
large_files = [f for f in glob.glob('*.csv') if os.path.getsize(f) > 15 * 1024 * 1024]

print(f"Tìm thấy các file lớn cần chia nhỏ: {large_files}")

for file_name in large_files:
    file_path = os.path.join(input_dir, file_name)
    base_name = os.path.splitext(file_name)[0]
    file_output_dir = os.path.join(output_dir, base_name)
    os.makedirs(file_output_dir, exist_ok=True)
    
    print(f"\nĐang tiến hành chia nhỏ file {file_name}...")
    batch_no = 1
    # Đọc chunk và ghi ra file
    for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
        output_file = os.path.join(file_output_dir, f'{base_name}_part_{batch_no}.csv')
        chunk.to_csv(output_file, index=False)
        # print(f'  Đã xuất thành công: {output_file}') # Comment lại để đỡ spam console
        batch_no += 1
    print(f"Đã chia {file_name} thành {batch_no - 1} files nhỏ.")

print("\nQuá trình hoàn tất! Bạn kiểm tra lại thư mục Split_Data nhé.")
