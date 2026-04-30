# Báo Cáo Chuyên Sâu: Doanh Thu & Giao Dịch (V2 - Datathon 2026 Finalist Edition)
**Dự án:** DATATHON 2026 – The Gridbreakers

---

## 0. Executive Summary (Tóm Tắt Thực Thi & Nhận Định Lõi)

Dựa trên phân tích toàn diện kho dữ liệu bán hàng giai đoạn 2013-2022, báo cáo tổng hợp (*Comprehensive Analytical Framework*) đã rút ra 3 phát hiện cốt lõi (*Key Highlights*) tác động trực tiếp đến định hướng chiến lược của doanh nghiệp:

1. **Bẫy lợi nhuận (*Profit Trap*):** Bất chấp doanh thu ổn định, biên lợi nhuận gộp liên tục "thủng đáy" xuống mức âm sâu (-40%) vào tháng 8 của các năm lẻ, và sụt giảm cực mạnh (còn 1-2%) vào tháng 12 hàng năm do đốt tiền vào chi phí cận Tết.
2. **Nghịch lý khuyến mãi (*Promotion Paradox*):** Việc lạm dụng mã giảm giá đang bào mòn giá trị giỏ hàng (*Cannibalization*). Đơn hàng có khuyến mãi có *AOV* (21.914 VNĐ) thấp hơn đến **20.5%** so với đơn mua thông thường (27.565 VNĐ), chứng tỏ khách hàng chỉ lợi dụng mã giảm giá để "săn deal" nhỏ lẻ thay vì mua sỉ.
3. **Tiềm năng thị trường ngách (*Niche Market Potential*):** Trái với quan niệm thông thường, sức mua (*Purchasing Power*) tại các tỉnh lẻ như Cẩm Phả, Thái Nguyên, Phủ Lý lại đang dẫn đầu, vượt mặt cả thủ đô Hà Nội. Cùng với đó, tập Khách VIP (Kim Cương, Vàng) tạo ra *AOV* vượt trội.

**Call to Action:** Chấm dứt chiến lược "Giảm giá đại trà" (*Mass Discounting*), chuyển dịch trục ngân sách sang đánh thẳng vào nhóm 25-44 tuổi tại các "tỉnh lẻ" và cá nhân hóa ưu đãi cho tệp Khách VIP.

---

## 1. Business Performance (Hiệu Quả Kinh Doanh & Bức Tranh Tài Chính)

### 1.1. Xu Hướng Doanh Thu (*Revenue Trend*)
Doanh thu của nền tảng chứng kiến chu kỳ biến động mạnh, chia làm hai giai đoạn:
- **Thời kỳ hoàng kim (2013-2016):** Tăng trưởng nóng và đạt đỉnh chu kỳ vào năm 2016 với xấp xỉ **2.1 tỷ VNĐ**.
- **Thời kỳ bão hòa và thoái trào (2019-2022):** Doanh thu lao dốc và đi ngang ở mức **1.0 - 1.1 tỷ VNĐ/năm**, bốc hơi gần một nửa so với đỉnh cao.

Về tính mùa vụ (*Seasonality*), quý 2 (Tháng 4, 5, 6) là giai đoạn "hốt bạc" của toàn sàn, phản ánh nhu cầu mua sắm tăng vọt đón đầu các đợt sale hè.

**Nguồn dữ liệu:** [`revenue_by_year.csv`](../Path2/revenue_by_year.csv), [`revenue_by_month.csv`](../Path2/revenue_by_month.csv)

<div style="page-break-inside: avoid; text-align: center; margin-bottom: 20px;">
  <img src="../Path2/Nop_Bai/Hien/4a_Revenue_Yearly.png" width="90%">
</div>
<div style="page-break-inside: avoid; text-align: center; margin-bottom: 20px;">
  <img src="../Path2/Nop_Bai/Hien/4b_Revenue_Monthly.png" width="90%">
</div>

### 1.2. Phân Tích Biên Lợi Nhuận Gộp (*Anomaly Detection*)
Mặc dù doanh thu có tính chu kỳ, nhưng **Biên lợi nhuận gộp (*Gross Margin*)** lại bộc lộ những "lỗ hổng" tài chính vô cùng nghiêm trọng. Biên lợi nhuận trung bình dao động quanh mức an toàn (10%-20%), nhưng đi kèm với 2 điểm bất thường (*Anomaly*):

1. **Chu kỳ thủng đáy Tháng 8 (Năm lẻ):** Cứ vào tháng 8 của các năm lẻ (2013, 2015, 2017, 2019, 2021), biên lợi nhuận rớt xuống mức **âm cực nặng (-30% đến -40%)**. Đây là dấu hiệu của việc "xả kho cắt lỗ" hoặc lỗi cấu hình giá có hệ thống.
2. **"Làm không công" vào Tháng 12:** Dù là mùa mua sắm lễ hội, lợi nhuận thực tế bị "bào mỏng" chỉ còn **1-2%**. Chi phí Marketing, Logistics và Khuyến mãi cuối năm đã ăn sạch phần lãi của doanh nghiệp.

**Nguồn dữ liệu:** [`6_Gross_Margin_Data.csv`](../Path2/Nop_Bai/Hien/6_Gross_Margin_Data.csv), [`6b_Gross_Margin_Seasonality_Data.csv`](../Path2/Nop_Bai/Hien/6b_Gross_Margin_Seasonality_Data.csv)

<div style="page-break-inside: avoid; text-align: center; margin-bottom: 20px;">
  <img src="../Path2/Nop_Bai/Hien/6a_Gross_Margin_Trend.png" width="90%">
</div>
<div style="page-break-inside: avoid; text-align: center; margin-bottom: 20px;">
  <img src="../Path2/Nop_Bai/Hien/6b_Gross_Margin_Seasonality.png" width="90%">
</div>

---

## 2. Customer Demographics & Channels (Nhân Khẩu Học & Nguồn Lưu Lượng)

Dữ liệu nhân khẩu học cho thấy doanh nghiệp đang khai thác rất tốt thị trường ngách thay vì bị cuốn vào "Đại dương đỏ".

1. **Nguồn truy cập (*Traffic Sources*):** Kênh **SEO** (Tối ưu hóa công cụ tìm kiếm tự nhiên) dẫn đầu với **28% tổng đơn hàng**. Khách hàng có thời gian lưu trang (*Session Duration*) vượt trội từ **107-213 giây** (hơn 3.5 phút), cho thấy ý định mua hàng (*Purchase Intent*) rất cao.
2. **Phân khúc độ tuổi (*Age Segmentation*):** Nhóm **25-44 tuổi** là *Core Target Audience* (Tệp khách chủ lực), chiếm **56%** khối lượng giao dịch. Một điểm sáng (*Highlight*) đáng ngạc nhiên là nhóm **55+ tuổi** lại có *Cancellation Rate* (Tỷ lệ hoàn/hủy đơn) cực thấp, chỉ ở mức **5.44%**, cho thấy sự cẩn trọng và trung thành của nhóm này.
3. **Giới tính & Địa lý (*Gender & Geographic Distribution*):** 
   - Tỷ lệ phân bổ rất cân bằng: Nữ (**48.9%**) và Nam (**47.1%**).
   - Về địa lý, thay vì tập trung ở các thành phố lớn, Top 5 khu vực có lượng khách đông nhất lại là: **Cẩm Phả (3.61%), Thái Nguyên (3.57%), Phủ Lý (3.48%), Hà Nội (3.48%) và Hạ Long (3.47%)**. Điều này chứng minh doanh nghiệp đã đánh chiếm thành công *Niche Market* (Thị trường ngách) tại các tỉnh lẻ với sức mua cực mạnh.

---

## 3. Customer Behavior (Hành Vi Thanh Toán & Chuyển Đổi)

### 3.1. Phân Bổ Điểm Chạm (*Touchpoints*)
Thiết bị **Mobile** đang thống trị nền tảng với **45.06%** lượng đơn hàng. Về thanh toán, **Thẻ tín dụng (Credit Card)** chiếm ưu thế (55.08%), chứng tỏ tệp khách hàng có thu nhập ổn định và quen thuộc với thanh toán số.

**Insights:** Dù Mobile dẫn đầu về lưu lượng, giao diện nhập liệu thẻ tín dụng trên màn hình nhỏ lại vô tình tạo ra *Friction Points* (Điểm ma sát), làm tăng tỷ lệ bỏ giỏ hàng (*Cart Abandonment*).

<div style="text-align: center; page-break-inside: avoid; margin-bottom: 20px;">
  <img src="../Path2/Nop_Bai/Hien/5a_Device_Behavior.png" width="48%" style="vertical-align: middle;">
  <img src="../Path2/Nop_Bai/Hien/5b_Payment_Methods.png" width="48%" style="vertical-align: middle;">
</div>

### 3.2. Hành Vi Trả Góp (*Buy Now, Pay Later - BNPL*)
Sự bùng nổ của *BNPL* được thể hiện qua việc **gần 60%** khách hàng sử dụng dịch vụ trả góp, đặc biệt là gói **Trả góp 3 tháng (33.8%)**. Điều này giúp giảm rào cản tâm lý khi mua các mặt hàng giá trị cao, tối ưu hóa tỷ lệ chuyển đổi (*Conversion Rate*).

<div style="page-break-inside: avoid; text-align: center; margin-bottom: 20px;">
  <img src="../Path2/Nop_Bai/Hien/5c_Installment_Behavior.png" width="90%">
</div>

---

## 4. Marketing Efficiency (Phễu Khách Hàng & Hiệu Suất Khuyến Mãi)

### 4.1. Nghịch Lý Khuyến Mãi (*Promotion Paradox*)
Khuyến mãi chiếm tới **38.4%** lượng đơn, nhưng dữ liệu lại đập tan lầm tưởng "Khuyến mãi giúp tăng AOV":

- Đơn **Không dùng khuyến mãi** có *AOV* đạt **27.565 VNĐ**.
- Đơn **Có dùng khuyến mãi** rớt thảm hại, chỉ còn **21.914 VNĐ**.

**Insights đính chính chiến lược:** Trái với quan điểm lý thuyết, khách hàng của doanh nghiệp đang có hành vi *"Cherry-picking"* (Săn deal). Khuyến mãi % không hề kích thích họ mua thêm, mà chỉ vô tình bào mòn lợi nhuận các mặt hàng giá rẻ. **Việc lạm dụng mã giảm % đang đi ngược lại hiệu quả kinh doanh.**

**Nguồn dữ liệu:** [`7_AOV_Promotion_Data.csv`](../Path2/Nop_Bai/Hien/7_AOV_Promotion_Data.csv)

<div style="text-align: center; page-break-inside: avoid; margin-bottom: 20px;">
  <img src="../Path2/Nop_Bai/Hien/7a_Promotion_Volume.png" width="48%" style="vertical-align: middle;">
  <img src="../Path2/Nop_Bai/Hien/7b_Promotion_AOV.png" width="48%" style="vertical-align: middle;">
</div>

### 4.2. Phân Tầng Khách Hàng (*Customer Tiering*)
- **New Acquisition (Khách Mới):** Chiếm tới **51%** nhưng chất lượng thấp (*AOV* vỏn vẹn **18.000 VNĐ**) và tỷ lệ rời bỏ cao.
- **Tập Khách Lõi (Vàng & Kim Cương):** Dù chỉ chiếm 24%, nhóm này tạo ra mức *AOV* khổng lồ (từ **32.000 đến 51.000 VNĐ**).

**Nguồn dữ liệu:** [`8_Customer_Tier_Data.csv`](../Path2/Nop_Bai/Hien/8_Customer_Tier_Data.csv)

<div style="page-break-inside: avoid; text-align: center; margin-bottom: 20px;">
  <img src="../Path2/Nop_Bai/Hien/8_Customer_Tier_Behavior.png" width="90%">
</div>

---

## 5. Prescriptive Analytics (Đề Xuất Chiến Lược Hành Động)

Sự giao thoa giữa dữ liệu nhân khẩu học và hiệu suất dòng tiền dẫn đến các hành động ưu tiên sau:

1. **Tối Ưu Ngân Sách Theo Vùng (*Geo-targeting*):** Điều hướng 80% *Ad Spend* (Ngân sách quảng cáo) vào nhóm 25-44 tuổi tại các "tỉnh lẻ" (Cẩm Phả, Thái Nguyên, Phủ Lý). Đây là tệp có dòng tiền ổn định và tránh được chi phí đấu thầu quảng cáo (*CPC*) đắt đỏ tại 2 thành phố lớn.
2. **Chiến Lược Giá (*Pricing Strategy*):** Xóa bỏ ngay các chương trình "Mass Discounting" (Giảm giá %) để ngăn chặn rủi ro *Cannibalization*. Chuyển trục sang *"Bundle Pricing"* (Mua combo giảm giá) hoặc *"Minimum Spend Threshold"* (Giảm 20K cho đơn từ 50K) nhằm ép khách hàng tăng *AOV*.
3. **Phòng Tuyến Tháng 8 & 12:** Khóa hệ thống chiết khấu tự động vào tháng 8 năm lẻ. Trong tháng 12, thay vì giảm sâu cắt máu, hãy bán nguyên giá nhưng tặng kèm *Exclusive Perks* (Dịch vụ gói quà VIP, Freeship hỏa tốc).
4. **Tối Ưu Điểm Chạm (UI/UX Mobile):** Loại bỏ *Friction Points* thanh toán thẻ trên Mobile bằng cách tích hợp One-tap Checkout (Apple Pay/Google Pay). Đồng thời làm nổi bật "Trả góp 0% kỳ hạn 3 tháng" để chốt chặn các mặt hàng có giá trị cao.
