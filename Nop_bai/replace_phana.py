import sys

with open(r'e:\project\datathon-2026-round-1\Nop_bai\Bao_Cao_Chien_Luoc_Toan_Dien_Datathon.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if line.startswith('## PHẦN A: BỨC TRANH DOANH THU & ĐỘNG LỰC THỊ TRƯỜNG'):
        start_idx = i
    if line.startswith('## PHẦN B: MÔ HÌNH DỰ BÁO & AI CÓ THỂ DIỄN GIẢI'):
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_content = """## PHẦN A: BỨC TRANH DOANH THU & ĐỘNG LỰC THỊ TRƯỜNG

> Tuyên ngôn chiến lược: Mọi phân tích trong báo cáo này đều hướng về một mục tiêu tối thượng — Bảo vệ biên lợi nhuận. Dữ liệu cho thấy mặc dù quy mô doanh thu đang duy trì sự ổn định, nhưng biên lợi nhuận cốt lõi lại đang chịu sự "bào mòn" nghiêm trọng từ các lỗ hổng trong khâu vận hành.

### A.1 Phân Tích Chu Kỳ Doanh Thu & Động Lực Tăng Trưởng

Phân tích chuỗi dữ liệu giao dịch trong 10 năm qua khắc họa một biểu đồ vòng đời doanh nghiệp trải qua 3 giai đoạn mang tính bước ngoặt, với sự dịch chuyển rõ rệt về động lực cốt lõi:

| Giai đoạn | Khung thời gian | Trạng thái Doanh thu | Động lực dẫn dắt |
|-----------|:---:|:---------:|---------------|
| **Bứt phá & Đạt đỉnh** | 2013 - 2016 | Đỉnh 2.1 tỷ VNĐ (2016) | Tăng trưởng dựa trên quy mô: Đạt ~82.000 đơn/năm. Danh mục Streetwear đóng vai trò lực kéo chủ lực với 1.69 tỷ VNĐ. |
| **Thoái trào & Sàng lọc** | 2019 - 2021 | Chạm đáy 1.0 tỷ VNĐ | Thu hẹp thị phần đại trà: Khối lượng đơn giảm sâu từ 70.000 xuống 34.000. Tuy nhiên, chỉ số AOV tăng vọt từ 25.000 lên 30.000 VNĐ. |
| **Phục hồi Cấu trúc** | 2022 | Khôi phục 1.16 tỷ VNĐ | AOV thiết lập đỉnh lịch sử 32.400 VNĐ. Streetwear tái khẳng định vị thế khi chiếm lĩnh 83.9% thị phần, kết hợp cùng Casual và GenZ tạo bệ phóng tăng trưởng mới. |

**Nhận định Quản trị:** Nhịp điều chỉnh giảm trong giai đoạn 2019-2021 không xuất phát từ một cuộc khủng hoảng toàn hệ thống. Bản chất của sự suy thoái này phản ánh rủi ro phụ thuộc vào phân khúc khách hàng VIP — tệp chỉ chiếm 9% quy mô nhưng duy trì mức AOV kỷ lục (51.000 VNĐ) — đi kèm với sự suy yếu trong năng lực thu hút và giữ chân người dùng mới.

<div style="page-break-inside: avoid; text-align: center; margin-top: 30px; margin-bottom: 20px;">
  <img src="./Images/4a_Revenue_Yearly.png" width="80%">
  <p><em>Hình A.1: Xu hướng tăng trưởng doanh thu theo năm (2013-2022) - 3 giai đoạn rõ rệt</em></p>
</div>

### A.2 Tính Mùa Vụ & Hiệu Ứng Cộng Hưởng

Dữ liệu lịch sử xác nhận Quý 2 (Tháng 4-5-6) luôn là đỉnh điểm doanh thu. Động lực này xuất phát từ hiệu ứng cộng hưởng kép: sự kiện ra mắt bộ sưu tập Xuân/Hè kết hợp chiến lược đẩy số qua các chiến dịch "Spring Sale" và "Mid-Year Sale".

Bộ ba danh mục cốt lõi GenZ, Streetwear, Casual thể hiện sức bật mạnh mẽ nhất trong giai đoạn này:

| Danh mục | Tốc độ tăng trưởng Q2 | Định vị chiến lược |
|----------|:------------------------:|---------|
| **GenZ** | +90.6% | Đầu tàu tạo xu hướng, thu hút dòng khách hàng trẻ. |
| **Streetwear** | +72.4% | Nhóm sinh lời chủ lực, đảm bảo thanh khoản hệ thống. |
| **Casual** | +70.4% | Phân khúc nền tảng, duy trì biên lợi nhuận an toàn. |

<div style="page-break-inside: avoid; text-align: center; margin-top: 30px; margin-bottom: 20px;">
  <img src="./Images/4b_Revenue_Monthly.png" width="48%" style="vertical-align: top;">
  <img src="./Images/4c_Category_Growth_Q2_Comprehensive.png" width="48%" style="vertical-align: top;">
  <p><em>Hình A.2: Đỉnh doanh thu Quý 2 (trái) và Bộ ba GenZ-Streetwear-Casual dẫn dắt tăng trưởng (phải)</em></p>
</div>

### A.3 Khủng Hoảng Suy Giảm Biên Lợi Nhuận Gộp

Bất chấp sự phục hồi về mặt doanh thu tổng, chỉ số Gross Margin đang phơi bày hai rạn nứt cấu trúc nghiêm trọng trong chiến lược định giá và khuyến mãi:

**Điểm gãy 1: Cái bẫy "Tháng 8 Năm Lẻ":**

| Khía cạnh | Tháng 8 năm chẵn | Tháng 8 năm lẻ |
|-----------|:-----------------:|:--------------:|
| Cấu trúc Khuyến mãi | Tỷ lệ phần trăm (Trung bình 10%) | Trợ giá cố định (Voucher 50.0 VNĐ) |
| Áp lực Chi phí | Trong ngưỡng an toàn | Bùng nổ gấp 10 lần |
| Gross Margin | +20% (Khỏe mạnh) | -35% (Thâm hụt nghiêm trọng) |

Khủng hoảng thâm hụt này không đến từ biến động thị trường, mà xuất phát 100% từ sai lầm trong thiết kế cấu trúc trợ giá.

<div style="page-break-inside: avoid; text-align: center; margin-top: 30px; margin-bottom: 20px;">
  <img src="./Images/6a_Gross_Margin_Trend.png" width="80%">
  <p><em>Hình A.3a: Sự suy giảm biên lợi nhuận qua các năm - "Tháng 8 Năm Lẻ" lộ diện rõ</em></p>
</div>

**Điểm gãy 2: Hiệu ứng tự ăn thịt doanh thu tại "Sale chồng Sale" Tháng 12:** Dù Tháng 12 là chu kỳ mua sắm bùng nổ, biên lợi nhuận lại bị nén chặt xuống mức 1-2%. Việc lạm dụng tần suất khuyến mãi dày đặc cùng sự phình to của chi phí tiếp thị dịp cận Tết đang ăn mòn hoàn toàn phần giá trị thặng dư tạo ra.

<div style="page-break-inside: avoid; text-align: center; margin-top: 30px; margin-bottom: 20px;">
  <img src="./Images/6b_Gross_Margin_Seasonality.png" width="80%">
  <p><em>Hình A.3b: Chu kỳ khủng hoảng biên lợi nhuận theo mùa - Tháng 8 & Tháng 12 là hai "hố đen"</em></p>
</div>

### A.4 Nhân Khẩu Học & Điểm Nghẽn Phễu Chuyển Đổi

#### Nguồn Truy Cập & Sự Trỗi Dậy Của Thị Trường Ngách

| Chỉ số trọng yếu | Giá trị | Hàm ý Kinh doanh |
|--------|:-------:|---------|
| Kênh dẫn dắt | **SEO** | Chiếm 28% lượng đơn hàng - tối ưu hóa cấu trúc chi phí tiếp thị. |
| Bounce Rate | **~47%** | Nằm trong vùng tối ưu, minh chứng luồng Trải nghiệm người dùng (UX) hiệu quả. |
| Phân khúc chủ lực | **25-44** | Đóng góp 56% khối lượng giao dịch, phản ánh tệp khách hàng có thu nhập ổn định. |
| Mở rộng địa lý | Cẩm Phả, Thái Nguyên, Biên Hòa | Sự chuyển dịch sức mua về các thị trường Cấp 2 và Cấp 3. |

<div style="page-break-inside: avoid; text-align: center; margin-top: 30px; margin-bottom: 20px;">
  <img src="./Images/5_Demographics_Traffic.png" width="95%">
  <p><em>Hình A.4a: Nhân khẩu học và Nguồn truy cập</em></p>
</div>

<div style="page-break-inside: avoid; text-align: center; margin-top: 30px; margin-bottom: 20px;">
  <img src="./Images/5b_Bounce_Rate_Traffic.png" width="60%">
  <p><em>Hình A.4b: Tỷ lệ thoát theo từng Kênh Truy Cập</em></p>
</div>

#### Nghịch lý Mobile - Điểm nghẽn tại Phễu thanh toán

Kênh Mobile đang dẫn đầu phễu thu hút khách hàng với 45.1% lưu lượng truy cập. Tuy nhiên, tỷ lệ từ bỏ giỏ hàng tại nền tảng này lại chạm ngưỡng báo động 68.5%. Kết hợp với thời lượng lưu trang trung bình lên tới 160 giây, dữ liệu minh chứng khách hàng có ý định mua sắm rất rõ ràng. Sự đứt gãy này chỉ ra điểm nghẽn nghiêm trọng về mặt UX tại bước thanh toán. Lực cản công nghệ đang làm gián đoạn hành trình mua, đòi hỏi Ban điều hành lập tức tối ưu hóa luồng thanh toán trên nền tảng di động.

<div style="page-break-inside: avoid; text-align: center; margin-top: 30px; margin-bottom: 20px;">
  <img src="./Images/5a_Device_Composite.png" width="100%">
  <p><em>Hình A.4c: Nghịch lý Mobile - Lưu lượng cao nhất nhưng tỷ lệ rớt đơn cũng cao nhất do những trở ngại khi thanh toán</em></p>
</div>

#### Cơ Cấu Thanh Toán & Đòn Bẩy Trả Góp

Hành vi thanh toán thể hiện mức độ số hóa cao khi Thẻ tín dụng chiếm áp đảo (55.1%), theo sau là hệ sinh thái ví điện tử như PayPal (15%) và Apple Pay (10%).

<div style="page-break-inside: avoid; text-align: center; margin-top: 30px; margin-bottom: 20px;">
  <img src="./Images/5b_Payment_Methods.png" width="70%">
  <p><em>Hình A.4d: Tỷ trọng Phương thức thanh toán</em></p>
</div>

**Định hình Chiến lược: BNPL như một Động lực Bán hàng:**

Dữ liệu xác nhận sự phụ thuộc mạnh mẽ vào đòn bẩy tài chính khi chỉ có 40.6% giao dịch được tất toán một lần. Gần 60% dòng tiền đang chảy qua các giải pháp BNPL, với kỳ hạn 3 tháng (33.8%) và 6-12 tháng (25.4%) chiếm ưu thế. Việc tích hợp BNPL đã vượt ra khỏi vai trò một cổng thanh toán đơn thuần, trở thành chiến lược giảm rào cản tâm lý về giá, giúp doanh nghiệp chốt đơn hiệu quả mà không cần lạm dụng chiết khấu sâu để bảo vệ lợi nhuận.

<div style="page-break-inside: avoid; text-align: center; margin-top: 30px; margin-bottom: 20px;">
  <img src="./Images/5c_Installment_Behavior.png" width="70%">
  <p><em>Hình A.4e: Hành vi Trả góp - 60% khách hàng phụ thuộc vào BNPL</em></p>
</div>

### A.5 Nghịch Lý Khuyến Mãi & Sự Bào Mòn Giá Trị

**Trợ giá sai mục tiêu gây suy giảm giá trị giỏ hàng**

Việc triển khai các chiến dịch khuyến mãi đang tạo ra phản ứng ngược. Mặc dù chiếm tới 38.4% tổng khối lượng đơn, nhóm giao dịch áp dụng mã giảm giá không những không gia tăng quy mô mua sắm mà còn trực tiếp kéo tụt chỉ số AOV xuống 20.5% (giảm từ 27.565 VNĐ xuống còn 21.914 VNĐ).

| Phân loại Đơn hàng | Mức AOV | Tác động Tài chính |
|----------|:---:|:----------:|
| **Nguyên giá** | 27.565 VNĐ | Mốc cơ sở |
| **Áp dụng Khuyến mãi** | 21.914 VNĐ | -20.5% ↓ Suy giảm giá trị |

Hành vi Cherry-picking của khách hàng — cố tình xé lẻ đơn hàng hoặc chỉ chọn các sản phẩm rẻ nhất để trục lợi mã giảm giá — đang biến công cụ kích cầu thành tác nhân gây loãng giá trị cốt lõi.

<div style="page-break-inside: avoid; text-align: center; margin-top: 30px; margin-bottom: 20px;">
  <img src="./Images/7a_Promotion_Volume.png" width="48%" style="vertical-align: top;">
  <img src="./Images/7b_Promotion_AOV.png" width="48%" style="vertical-align: top;">
  <p><em>Hình A.5a: AOV sụt giảm rõ rệt khi có khuyến mãi - minh chứng cho "Promotion Paradox"</em></p>
</div>

**Phân tích Đa biến: Tương quan Khuyến mãi & Biên lợi nhuận ròng:**

> **Công thức:** Biên Lợi Nhuận Ròng = (Lợi nhuận ròng / Tổng doanh thu)

| Chiến dịch | Biên Lợi Nhuận | Phân Loại Rủi Ro |
|:---|:---:|:---|
| **Urban Blowout** | -62.5% | Lỗ thảm họa |
| **Year-End Sale** | -19.6% | Thâm hụt tài chính nặng nề |
| **Mid-Year Sale** | -15.7% | Bào mòn ngân sách |
| **Rural Special** | -7.4% | Phá vỡ điểm hòa vốn |
| **Spring Sale** | -2.9% | Rủi ro xói mòn lợi nhuận |
| **Fall Launch** | +0.8% | Duy trì thặng dư tối thiểu |

**Hàm ý Quản trị:** Dữ liệu kiểm toán từ 6 chiến dịch trọng điểm bóc trần một thực trạng nguy hiểm: Doanh nghiệp đang mua tăng trưởng doanh thu bằng cái giá của lợi nhuận ròng. Ngoại trừ chiến dịch Fall Launch duy trì mức thặng dư mong manh (+0.8%), 5 chiến dịch còn lại đều tiêu hao ngân sách trầm trọng, đỉnh điểm là Urban Blowout với mức phá hủy giá trị lên tới -62.5%. Khuyến nghị Ban điều hành lập tức tái thiết kế cấu trúc khuyến mãi, chuyển từ chiến lược chiết khấu đại trà sang chiến lược bán chéo (Cross-selling / Bundling).

<div style="page-break-inside: avoid; text-align: center; margin-top: 30px; margin-bottom: 20px;">
  <img src="./Images/9a_Promotion_Profit_Margin.png" width="90%">
  <p><em>Hình A.5b: Phân tích Promotion vs Profit Margin - hầu hết chiến dịch đang "đốt tiền"</em></p>
</div>

### A.6 Cấu Trúc Phân Tầng Khách Hàng & Rủi Ro Tập Trung

| Phân Tầng | Tỷ Trọng | Đóng Góp AOV | Định Vị Chân Dung |
|:---|:---:|:---:|:---|
| **Khách Mới** | 51% | 18.000 VNĐ | Quy mô phủ sóng rộng nhưng tỷ lệ rớt phễu cao, mức độ sinh lời thấp. |
| **Khách Bạc** | 25% | 24.000 VNĐ | Giai đoạn chuyển tiếp, bắt đầu thiết lập thói quen tiêu dùng. |
| **Khách Vàng** | 15% | 32.000 VNĐ | Tệp khách hàng nòng cốt, tạo dòng tiền đều đặn. |
| **Khách Kim Cương** | 9% | 51.000 VNĐ | Trụ cột thanh khoản, sức chi trả gấp gần 3 lần tệp Khách Mới. |

**Cảnh Báo Rủi Ro Tập Trung:**
Cấu trúc phễu khách hàng hiện tại đang tiềm ẩn sự bất cân xứng nghiêm trọng. Mặc dù nhóm Khách Mới thống trị về mặt số lượng (51%), khả năng chuyển hóa thành doanh thu thực tế lại cực kỳ mờ nhạt. Toàn bộ trọng trách duy trì dòng tiền đang đè nặng lên vai tệp Khách Kim Cương — nhóm chỉ chiếm vỏn vẹn 9% nhưng có sức mua áp đảo. Trạng thái phân bổ này đẩy doanh nghiệp vào mức độ rủi ro tập trung cao độ; bất kỳ biến động nhỏ nào làm suy giảm tỷ lệ giữ chân của tệp 9% VIP này cũng sẽ gây chấn động lập tức đến cấu trúc lợi nhuận toàn hệ thống.

<div style="page-break-inside: avoid; text-align: center; margin-top: 30px; margin-bottom: 20px;">
  <img src="./Images/8_Customer_Tier_Behavior.png" width="90%">
  <p><em>Hình A.6: Chênh lệch AOV giữa các Phân tầng Khách hàng - VIP 9% chi phối toàn bộ dòng tiền</em></p>
</div>

---

"""
    
    lines[start_idx:end_idx] = [new_content]
    
    with open(r'e:\project\datathon-2026-round-1\Nop_bai\Bao_Cao_Chien_Luoc_Toan_Dien_Datathon.md', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print('Replacement successful.')
else:
    print('Failed to find start or end indices.')
    print('start_idx:', start_idx, 'end_idx:', end_idx)
