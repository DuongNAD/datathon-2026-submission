import pandas as pd
import os
import glob

base_path = r"e:\project\datathon-2026-round-1\Analysis"

# Đã có sẵn file category_yearly_full.csv chứa toàn bộ thông tin của category qua các năm.
# Đây chính là file "gộp các category_info thành 1 file"
full_file_path = os.path.join(base_path, "category_yearly_full.csv")

if os.path.exists(full_file_path):
    print(f"Đang đọc file gộp chung: {full_file_path}")
    df = pd.read_csv(full_file_path)
    
    # Lấy danh sách các category
    categories = df['Danh Mục'].dropna().unique()
    
    print("Đang tạo các file riêng cho từng category...")
    for cat in categories:
        # Lọc dữ liệu theo từng category
        df_cat = df[df['Danh Mục'] == cat]
        
        # Tạo tên file hợp lệ (loại bỏ ký tự đặc biệt nếu có)
        safe_cat_name = str(cat).replace('/', '_').replace('\\', '_')
        output_file = os.path.join(base_path, f"category_{safe_cat_name}.csv")
        
        # Lưu file
        df_cat.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"- Đã lưu: {output_file}")
        
    # (Tùy chọn) Xóa các file category_info_<năm>.csv cũ vì đã được gộp
    old_files = glob.glob(os.path.join(base_path, "category_info_*.csv"))
    for old_f in old_files:
        try:
            os.remove(old_f)
        except Exception as e:
            pass
    print("Đã dọn dẹp các file từng năm lẻ tẻ.")
    print("Hoàn tất!")
else:
    print(f"Không tìm thấy file {full_file_path}")
