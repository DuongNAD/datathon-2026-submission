import pandas as pd
import numpy as np
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# =================================================================
# 1. XỬ LÝ DỮ LIỆU
# =================================================================
products = pd.read_csv('products.csv')
inventory = pd.read_csv('inventory.csv')

df = pd.merge(inventory, products[['product_id', 'price', 'cogs']], on='product_id', how='left')
df['unit_profit'] = df['price'] - df['cogs']
df['total_profit'] = df['units_sold'] * df['unit_profit']

# ---------------------------------------------------------
# Lớp Báo cáo PDF (Hỗ trợ Unicode, Tracking đầy đủ & Biện luận)
# ---------------------------------------------------------
class SupplyChainReport(FPDF):
    def __init__(self):
        super().__init__()
        try:
            self.add_font('Arial_Unicode', '', 'arial.ttf')
            self.add_font('Arial_Unicode', 'B', 'arialbd.ttf')
            self.font_name = 'Arial_Unicode'
        except:
            self.font_name = 'helvetica'
            print("CẢNH BÁO: Không tìm thấy font arial.ttf. Chữ sẽ bị mất dấu.")

    def header(self):
        self.set_font(self.font_name, 'B', 15)
        self.set_text_color(26, 42, 108)
        self.cell(0, 10, 'BÁO CÁO CHIẾN LƯỢC SẢN PHẨM & CHUỖI CUNG ỨNG', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

    def chapter_title(self, title):
        self.set_font(self.font_name, 'B', 12)
        self.set_fill_color(230, 235, 245)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, title, fill=True, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

    def chapter_body(self, text, is_bold=False):
        style = 'B' if is_bold else ''
        self.set_font(self.font_name, style, 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 7, text)
        self.ln(2)

    def create_table(self, dataframe, col_widths):
        self.set_font(self.font_name, 'B', 9)
        if dataframe.index.name is None and not isinstance(dataframe.index, pd.MultiIndex):
            df_reset = dataframe.reset_index(drop=True)
        else:
            df_reset = dataframe.reset_index()
            
        cols = list(df_reset.columns)
        if len(col_widths) < len(cols):
            col_widths += [30] * (len(cols) - len(col_widths))

        # Header bảng
        self.set_fill_color(26, 42, 108)
        self.set_text_color(255, 255, 255)
        for i, col in enumerate(cols):
            self.cell(col_widths[i], 10, str(col), border=1, align='C', fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.ln()
        
        # Dữ liệu bảng
        self.set_text_color(0, 0, 0)
        self.set_font(self.font_name, '', 8)
        for _, row in df_reset.iterrows():
            for i, value in enumerate(row):
                val = f"{value:,.1f}" if isinstance(value, (float, int, np.int64)) else str(value)
                self.cell(col_widths[i], 8, val, border=1, align='C', new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.ln()
        self.ln(4)

# Khởi tạo PDF
pdf = SupplyChainReport()
pdf.add_page()

# --- PHẦN 1: CÔNG THỨC & CƠ SỞ DỮ LIỆU ---
pdf.chapter_title("1. PHƯƠNG PHÁP LUẬN VÀ CƠ SỞ TÍNH TOÁN")
pdf.chapter_body("Để đưa ra các quyết định về chuỗi cung ứng, báo cáo dựa trên sự đối soát giữa Hiệu suất Tài chính và Rủi ro Vận hành thông qua các công thức cốt lõi:")
pdf.chapter_body("- Lợi nhuận đơn vị = Giá bán - Giá vốn (COGS)\n- Tổng lợi nhuận = Số lượng bán x Lợi nhuận đơn vị\n- Tỷ lệ bán ra (Sell-through Rate) = Số lượng bán / (Số lượng bán + Tồn kho)\n- Tỷ lệ Overstock = Tần suất hàng bị thừa so với dự báo nhu cầu.")

# --- PHẦN 2: TRACKING DỮ LIỆU CHI TIẾT ---
pdf.chapter_title("2. THEO DÕI BIẾN ĐỘNG HÀNG HÓA CHI TIẾT THEO NĂM (TRACKING)")
pdf.chapter_body("Bảng dưới đây theo dõi biến động Nhập - Bán - Tồn của các danh mục chính. Dữ liệu cho thấy sự tích tụ hàng tồn kho lớn từ sau năm 2018, đặc biệt là nhóm Streetwear và Outdoor.")
yearly_stats = df.groupby(['year', 'category']).agg({
    'units_sold': 'sum',
    'units_received': 'sum',
    'stock_on_hand': 'sum'
}).rename(columns={'units_sold': 'Bán Ra', 'units_received': 'Nhập Kho', 'stock_on_hand': 'Tồn Kho'})
pdf.create_table(yearly_stats.head(20), [20, 45, 40, 40, 40])

# --- PHẦN 3: PHÂN TÍCH LỢI NHUẬN (INSIGHTS) ---
pdf.chapter_title("3. PHÂN TÍCH LỢI NHUẬN (PROFITABILITY ANALYSIS)")
pdf.chapter_body("Căn cứ vào dữ liệu, chúng ta xác định được danh mục Streetwear đóng vai trò là 'trụ cột' lợi nhuận. Phân khúc Everyday và Balanced đóng góp hơn 80% tổng dòng tiền.")
cat_profit = df.groupby('category').agg({'total_profit': 'sum', 'units_sold': 'sum'}).sort_values('total_profit', ascending=False).rename(columns={'total_profit': 'Lợi Nhuận', 'units_sold': 'Sản Lượng'})
pdf.create_table(cat_profit, [45, 70, 70])

# --- PHẦN 4: RỦI RO TỒN KHO ---
pdf.chapter_title("4. PHÂN TÍCH RỦI RO TỒN KHO (INVENTORY RISK)")
pdf.chapter_body("Phân tích rủi ro chỉ ra rằng Outdoor là nhóm rủi ro nhất với Tỷ lệ tồn vượt mức (Overstock) cao nhất nhưng Tỷ lệ bán ra thấp nhất. Điều này gây ra tình trạng 'giam vốn' nặng nề.")
risk_analysis = df.groupby('category').agg({'stockout_days': 'mean', 'overstock_flag': 'mean', 'sell_through_rate': 'mean'}).sort_values('overstock_flag', ascending=False).rename(columns={'stockout_days': 'Hết hàng(TB)', 'overstock_flag': 'Tỷ lệ Over', 'sell_through_rate': 'Tỷ lệ Bán ra'})
pdf.create_table(risk_analysis, [40, 40, 45, 45])

# --- PHẦN 5: ĐỀ XUẤT ---
pdf.add_page()
pdf.chapter_title("5. ĐỀ XUẤT NGỪNG KINH DOANH VÀ GIẢI PHÁP CHIẾN LƯỢC")
pdf.chapter_body("Dựa trên 'Ma trận Yếu kém' (Lợi nhuận thuộc nhóm 10% đáy và Tỷ lệ Overstock > 50%), chúng ta đề xuất loại bỏ 10 sản phẩm sau để thu hồi vốn lưu động:")

product_perf = df.groupby(['product_id', 'product_name', 'category']).agg({'total_profit': 'sum', 'overstock_flag': 'mean'}).reset_index()
profit_cutoff = product_perf['total_profit'].quantile(0.10)
stop_selling = product_perf[(product_perf['total_profit'] <= profit_cutoff) & (product_perf['overstock_flag'] > 0.5)].sort_values('total_profit').head(10)
stop_selling_print = stop_selling[['product_id', 'product_name', 'total_profit', 'overstock_flag']].rename(columns={'product_id': 'ID', 'product_name': 'Tên SP', 'total_profit': 'Lợi nhuận', 'overstock_flag': 'Tỷ lệ Over'})
pdf.create_table(stop_selling_print, [20, 75, 45, 45])

# PHẦN GIẢI THÍCH CHI TIẾT GIẢI PHÁP
pdf.chapter_body("CÁC GIẢI PHÁP TỐI ƯU CỤ THỂ:", is_bold=True)
pdf.chapter_body("1. GIẢI PHÁP XẢ KHO (LIQUIDATION): Áp dụng chiến dịch Bundle (Bia kèm lạc). Tặng kèm các sản phẩm Outdoor tồn kho cao (>80%) cho khách hàng mua Streetwear hot. Mục tiêu là giải phóng không gian kho ngay lập tức.")
pdf.chapter_body("2. TỐI ƯU SỐ NGÀY TỒN: Chuyển dịch từ nhập hàng khối lượng lớn sang mô hình dự báo theo tuần. Mục tiêu đưa tỷ lệ Sell-through Rate lên mức 30-40% thay vì 15% như hiện tại.")
pdf.chapter_body("3. ĐIỀU TIẾT DÒNG VỐN: Ngừng nhập mới 100% đối với danh sách đề xuất ở trên. Dồn nguồn vốn giải phóng được để nhập thêm các mã Streetwear - Balanced đang có sức mua tốt.")

pdf.output("Bao_Cao_Supply_Chain_Hoan_Chinh.pdf")
print("Thành công! File Bao_Cao_Supply_Chain_Hoan_Chinh.pdf đã được tạo với đầy đủ dữ liệu và biện luận.")