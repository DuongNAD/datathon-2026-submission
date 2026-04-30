# Báo cáo Kỹ thuật - Mô hình Dự báo Doanh thu (Sales Forecasting)

Báo cáo này trình bày chi tiết về luồng xử lý dữ liệu, phương pháp mô hình hoá và đánh giá tầm quan trọng của các đặc trưng nhằm giải quyết bài toán Dự báo Doanh thu (Phần 3). Toàn bộ pipeline này được xây dựng trên nguyên tắc tuân thủ nghiêm ngặt tính tái lập và tuyệt đối không rò rỉ dữ liệu (Data Leakage).

---

## 1. Xử lý Rò rỉ Dữ liệu (Data Leakage)
Bài toán yêu cầu dự báo khoảng thời gian từ `01/01/2023` đến `01/07/2024` (tương lai 18 tháng). 
**Nhận định rủi ro:** Các dữ liệu từ file `promotions.csv`, `orders.csv`, `web_traffic.csv` chỉ có sẵn đến cuối năm 2022. Nếu sử dụng các file này để nội suy làm feature thì thực tế ở thời điểm dự báo (2023-2024) chúng ta sẽ không có những dữ liệu này, dẫn đến sai số trầm trọng khi chạy thực tế (Data Leakage).
**Chiến lược giải quyết:** Mô hình chỉ sử dụng hoàn toàn các **đặc trưng thời gian (Time-based Features)** và **lịch sự kiện cố định (Deterministic Events)**. Tất cả các tính năng này có thể suy ra tự động cho mọi mốc thời gian trong tương lai mà không cần thông tin bên ngoài.

---

## 2. Kỹ nghệ Đặc trưng (Feature Engineering)
Tập hợp đặc trưng bao gồm:
1. **Time-based Features:** `year`, `month`, `day`, `day_of_week`, `day_of_year`, `quarter`.
2. **Time Flags:** `is_weekend`, `is_month_start`, `is_month_end`.
3. **Sự kiện Mega Sales (Dương lịch):** Các ngày lễ/sự kiện cố định tạo ra đột biến doanh thu được tạo ra dựa trên ngày/tháng (ví dụ: 14/2, 8/3, 11/11, Black Friday).
4. **Hiệu ứng Tết Âm Lịch (Lunar New Year):** 
   - Tết Nguyên Đán là yếu tố gây ra nhiễu động lớn nhất cho các doanh nghiệp bán lẻ tại VN. Do lịch Âm thay đổi mỗi năm so với Dương lịch nên các mô hình sử dụng "tháng" cố định sẽ thất bại.
   - Thư viện `holidays` được sử dụng để trích xuất ngày Tết. Mô hình tạo ra biến đếm ngược `days_to_tet` để bắt chính xác sóng "mua sắm cận Tết" (thường bùng nổ trước Tết từ 2-3 tuần).

---

## 3. Kiến trúc Mô hình (Hybrid Model Architecture)
Các mô hình dạng cây (Tree-based) như LightGBM, XGBoost cực kỳ hiệu quả trong việc tìm ra tính thời vụ và sự tương tác phức tạp giữa các đặc trưng, nhưng chúng có nhược điểm lớn là **không thể ngoại suy (Extrapolation)** xu hướng dài hạn. Để giải quyết, chúng tôi sử dụng mô hình lai:

1. **Linear Regression (Bắt Trend):** Hồi quy doanh thu dựa trên index thời gian để tìm ra đường cơ sở (Baseline Trend) của sự tăng trưởng hoặc suy giảm doanh thu qua các năm.
2. **Tính Residuals (Phần dư):** Lấy `Doanh thu thực tế` trừ đi `Dự báo Trend`.
3. **LightGBM (Bắt Tính Thời vụ):** Huấn luyện LightGBM trên phần Residuals này dựa trên các feature thời gian và sự kiện ở phần 2. LightGBM (Gradient Boosting) có khả năng xử lý rất tốt các biến Categorical.
4. **Kết hợp:** `Dự báo Cuối cùng` = `Dự báo Linear` + `Dự báo LightGBM`.

### Cross-Validation
Sử dụng phương pháp **Time-series Split** phù hợp với bài toán chuỗi thời gian:
- Huấn luyện mô hình (Train) từ `2012` đến `2021`.
- Kiểm định (Validation) trên năm gần nhất `2022`. Đo lường MAE, RMSE, R² để tinh chỉnh siêu tham số.
- Sau khi chốt mô hình, toàn bộ dữ liệu 2012-2022 sẽ được dùng để Retrain nhằm có sức mạnh dự báo cao nhất cho tập Test.

---

## 4. Xử lý Logic Kinh doanh cho COGS
Nếu dùng Machine Learning dự báo độc lập cả `Revenue` và `COGS`, mô hình có thể dự đoán những điểm dị biệt mà ở đó Giá vốn (COGS) lại cao hơn Doanh thu (bán lỗ vốn diện rộng). Để đảm bảo an toàn về mặt logic kế toán và kinh doanh:
- COGS sẽ được suy ra từ Revenue thông qua tỷ suất lợi nhuận cận biên trong quá khứ.
- `Margin_Ratio` được tính từ tổng `COGS` chia tổng `Revenue` của năm gần nhất (2022).
- `Dự báo COGS` = `Dự báo Revenue` * `Margin_Ratio`.

---

## 5. Khả năng Giải thích (Explainability) bằng SHAP
Thông qua phân tích Feature Importance và SHAP values từ mô hình, những yếu tố tác động lớn nhất đến doanh thu bao gồm:
- **`days_to_tet` (Ngày cận Tết):** Yếu tố mạnh nhất. Càng tiến dần về giá trị 0 (ngày Tết), tác động dương đến doanh thu càng lớn.
- **Tính thời vụ (`month`, `day_of_year`):** Doanh thu có chu kỳ biến động lớn giữa các tháng, đặc biệt là các tháng cuối năm và đầu năm.
- **Mega Sales (`is_mega_sale`):** SHAP cho thấy tại những ngày như 11/11, 12/12, giá trị phần dư bùng nổ vượt khỏi mức trung bình một cách mạnh mẽ.

*(Lưu ý: Các biểu đồ chi tiết về LightGBM Feature Importance và SHAP Summary Plot được tạo ra trực tiếp trong Jupyter Notebook được đính kèm `advanced_model.ipynb`).*
