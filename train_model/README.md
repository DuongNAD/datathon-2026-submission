# 🏆 Datathon 2026 — The Gridbreakers

> **Dự báo Doanh thu & Giá vốn hàng bán** cho một doanh nghiệp thời trang e-commerce Việt Nam.  
> Cuộc thi tổ chức bởi VinTelligence — VinUniversity DS&AI Club.

---

## ⚡ Quick Start — Tái Lập Kết Quả (One-Click Run)

```bash
# 1. Cài đặt thư viện (phiên bản đã pinned)
pip install -r requirements.txt

# 2. Chạy pipeline huấn luyện + dự báo + SHAP
python scripts/train_v6.py

# 3. Kiểm tra ràng buộc submission
python scripts/check_constraints.py
```

> **Lưu ý:** Script tự động resolve đường dẫn — có thể chạy từ **bất kỳ thư mục nào**.  
> Output: `submission_v6.csv` (548 dòng, format khớp `sample_submission.csv`).

---

## 📁 Cấu Trúc Thư Mục

```
train_model/
├── dataset/                        # Dữ liệu (KHÔNG CHỈNH SỬA)
│   ├── sales_train.csv             #   Train: 04/07/2012 → 31/12/2022 (3,833 ngày)
│   └── sales_test.csv              #   Test:  01/01/2023 → 01/07/2024 (548 ngày)
│
├── scripts/                        # Mã nguồn chính
│   ├── train_v6.py                 #   🔥 Pipeline chính (Feature Eng → LightGBM → SHAP)
│   ├── check_constraints.py        #   Kiểm tra ràng buộc đề thi
│   └── evaluate.py                 #   Đánh giá mô hình trên tập validation
│
├── model_v6/                       # Artifacts của mô hình v6
│   ├── lgbm_rev_seed{42,...}.txt   #   5 boosters Revenue (Ensemble)
│   ├── lgbm_gm_seed{42,...}.txt    #   5 boosters Gross Margin %
│   ├── features.json               #   Danh sách 40 features
│   ├── validation_metrics.json     #   Metrics: R²=0.80, MAE=531K, MAPE=21.1%
│   ├── shap_summary_real.png       #   SHAP Beeswarm Plot
│   ├── shap_bar_real.png           #   SHAP Bar Plot
│   └── shap_importances.json       #   SHAP values cho từng feature
│
├── submission_v6.csv               # 📤 File nộp Kaggle (548 dòng)
├── requirements.txt                # Thư viện + phiên bản (pinned)
└── README.md                       # File này
```

---

## 🧠 Kiến Trúc Mô Hình v6

### Pipeline

```
sales_train.csv
    │
    ▼
┌──────────────────────────────────┐
│  Feature Engineering (40 biến)   │
│  Calendar + Fourier + Tet/Holiday│
│  + Lag(1,7,30,364,365)           │
│  + Rolling Mean(7d, 30d)         │
│  + Month-end spike zone          │
└──────────┬───────────────────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
┌────────┐  ┌──────────┐
│Revenue │  │ GM%      │
│Model   │  │ Model    │
│(log)   │  │          │
└───┬────┘  └────┬─────┘
    │            │
    ▼            ▼
  Revenue    COGS = Revenue × (1 - GM%)
    │            │
    └─────┬──────┘
          ▼
   submission_v6.csv
```

### Chi tiết kỹ thuật

| Thành phần | Mô tả |
|-----------|-------|
| **Thuật toán** | LightGBM (GBDT) |
| **Target transform** | `log1p(Revenue)` → `expm1` khi predict |
| **Ensemble** | 5 seeds × 2 models (Revenue + GM%) = 10 boosters |
| **Validation** | Hold-out temporal: train → 30/06/2021, val → 31/12/2022 |
| **COVID handling** | Giảm trọng số (weight=0.3) cho giai đoạn giãn cách |
| **Explainability** | SHAP TreeExplainer trên tập validation |

### Top 5 Features (SHAP)

| # | Feature | Mô tả | mean(\|SHAP\|) |
|:-:|---------|-------|:--------------:|
| 1 | `revenue_lag_1` | Doanh thu ngày hôm trước | 0.306 |
| 2 | `revenue_lag_365` | Doanh thu cùng kỳ năm trước | 0.061 |
| 3 | `revenue_lag_364` | Doanh thu cùng kỳ -1 ngày | 0.055 |
| 4 | `days_to_month_end` | Số ngày đến cuối tháng | 0.048 |
| 5 | `revenue_rolling_30` | Trung bình 30 ngày gần nhất | 0.042 |

---

## 📊 Hiệu Suất Mô Hình

### Validation (Hold-out: 07/2021 → 12/2022, 549 ngày)

| Metric | Giá trị |
|--------|:-------:|
| **R²** | 0.7978 |
| **MAE** | 531,042 |
| **RMSE** | 698,857 |
| **MAPE** | 21.1% |

| Giai đoạn | R² | MAPE |
|:---------:|:--:|:----:|
| Nửa cuối 2021 | 0.64 | 23.0% |
| Năm 2022 | 0.80 | 20.1% |

---

## 🔒 Tuân Thủ Ràng Buộc Đề Thi

| # | Ràng buộc | Trạng thái |
|:-:|-----------|:----------:|
| 1 | Không dùng Revenue/COGS từ tập test làm feature | ✅ |
| 2 | Không dùng dữ liệu ngoài bộ được cung cấp | ✅ |
| 3 | Đính kèm mã nguồn, kết quả tái lập được | ✅ |
| 4 | Random seeds cố định `[42, 123, 777, 2026, 314]` | ✅ |
| 5 | SHAP explainability | ✅ |
| 6 | Cross-validation đúng chiều thời gian | ✅ |

---

## 📎 Liên Kết

- **Kaggle:** [datathon-2026-round-1](https://www.kaggle.com/competitions/datathon-2026-round-1)
- **Báo cáo chiến lược:** Xem file `Nop_bai/Bao_Cao_Chien_Luoc_Toan_Dien_Datathon.pdf`
