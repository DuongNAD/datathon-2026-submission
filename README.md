# Datathon 2026 — Vòng 1 | The Gridbreakers

**Đề tài:** Dự báo Doanh thu (Revenue) và Giá vốn hàng bán (COGS) cho doanh nghiệp thời trang e-commerce Việt Nam.  
**Cuộc thi:** Tổ chức bởi VinTelligence — VinUniversity DS&AI Club.  
**Kết quả:** **Public Leaderboard RMSE = 740,764**

---

## Hướng Dẫn Tái Lập Kết Quả

Toàn bộ pipeline có thể tái lập 100% bằng 3 dòng lệnh:

```bash
cd train_model
pip install -r requirements.txt
python scripts/train_v55_ultimate.py
```

Random seeds cố định: `[42, 123, 777]` — đảm bảo kết quả giống hệt mỗi lần chạy.

---

## Hiệu Suất Mô Hình

### Top Models (Public Leaderboard)

| Rank | Model | RMSE | Multiplier | Mô tả |
|:----:|-------|:----:|:----------:|-------|
| 1 | **V55 Ensemble** | **740,764** | 1.28 | 18 models (LGB+XGB+CatBoost+RF) × 3 seeds, blend 90/10 |
| 2 | V55 Fine-tune | ~741K | 1.275–1.285 | Grid search quanh điểm tối ưu |
| 3 | V62 Precision | ~741K | 1.278 | Smearing correction + COGS ensemble 18 models |
| 4 | V58 Deep Trees | 743K | 1.28 | 127 leaves — overfitting nhẹ |
| 5 | V56 Titan | ~750K | 1.28 | Thêm growth features — noise do structural break |
| 6 | V60 Ridge Hybrid | 769K | 1.28 | Ridge trend ngoại suy sai |
| 7 | V37 Nova | 780K | 1.19 | LightGBM đơn, 1 seed |
| 8 | V54 Pinnacle | ~800K | 1.20 | Ensemble trước khi tìm ra m=1.28 |
| — | Naive Baseline | > 900K | — | DOY mean, không trend correction |

### Best Submissions (Nộp Kaggle)

| File | Chiến lược | Dùng cho |
|------|-----------|----------|
| `submission_v55_m128.csv` | Best confirmed RMSE = 740,764 | **Final submission chính** |
| `submission_v62_fine_1278.csv` | Hedge multiplier thấp hơn, COGS ensemble mới | Submission dự phòng |

---

## Kiến Trúc Mô Hình — V55 Hybrid Ensemble

```
┌─────────────────────────────────────────────────────────┐
│                    INPUT: 41 Features                   │
│  Fourier (16) + Lags (10) + Seasonal Mean (4) + Cal(11)│
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ Seed 42  │  │ Seed 123 │  │ Seed 777 │
   │ 6 models │  │ 6 models │  │ 6 models │
   └────┬─────┘  └────┬─────┘  └────┬─────┘
        └──────────────┼─────────────┘
                       ▼
              Weighted Average (18 models)
         LGB(25%) + XGB(25%) + CatBoost(30%)
              + RandomForest(10%) + MAE(10%)
                       │
                       ▼
           ┌───────────────────────┐
           │  Hybrid Blending      │
           │  90% ML + 10% Naive   │
           └───────────┬───────────┘
                       │
                       ▼
           ┌───────────────────────┐
           │  Trend Multiplier     │
           │  α = 1.28             │
           └───────────┬───────────┘
                       │
                       ▼
              Final Revenue Prediction
```

**Công thức dự báo:**

```
Revenue_t = 1.28 × [ 0.9 × expm1(ŷ_ML) + 0.1 × ŷ_Naive ]
COGS_t   = Revenue_t × clip(COGS_Ratio, 0.65, 0.95)
```

### 6 Loại Base Model

| # | Model | Loss | Weight | Rounds |
|---|-------|------|:------:|:------:|
| 1 | LightGBM | RMSE | 25% | 800 |
| 2 | LightGBM | MAE | 10% | 800 |
| 3 | XGBoost | MSE | 25% | 800 |
| 4 | CatBoost | RMSE | 20% | 800 |
| 5 | CatBoost | MAE | 10% | 800 |
| 6 | Random Forest | — | 10% | 400 trees |

### 41 Features (Thuần Thời Gian)

- **Fourier Transforms (16):** Chu kỳ 365.25 ngày (bậc 1–4), 30.5 ngày (bậc 1–2), 7 ngày (bậc 1–2)
- **Lag đa tầng (10):** DOY-aligned (365, 730) + DOW-aligned (364, 728) + COGS lags
- **Seasonal Mean (4):** Trung bình Revenue theo `dayofyear`, `weekofyear`, tháng, thứ
- **Calendar & Events (11):** `time_idx`, `is_payday`, `is_double_day`, `is_month_end`, `is_weekend`, interactions

### Anti-Leakage

- Revenue/COGS test **không bao giờ** xuất hiện trong features
- Lag features chỉ truy xuất từ train set
- Sample weights: `w = exp(-0.15 × (2023 - year))` — ưu tiên gần nhưng giữ seasonal dài hạn
- Không dùng dữ liệu ngoài (chỉ `sales_train.csv`)

---

## Cấu Trúc Thư Mục

```
datathon-2026-round-1/
│
├── train_model/                           Pipeline học máy
│   ├── scripts/
│   │   ├── train_v55_ultimate.py             Best model (RMSE=740,764)
│   │   ├── train_v62_precision.py            Precision tuning + COGS ensemble
│   │   ├── train_v61_endgame.py              Hedge strategy (time-varying multiplier)
│   │   ├── train_v37_nova.py                 Baseline LightGBM (RMSE~780K)
│   │   ├── train_v6.py                       Initial pipeline (R²=0.80)
│   │   ├── check_constraints.py              Kiểm tra ràng buộc đề thi
│   │   └── evaluate.py                       Đánh giá mô hình trên validation
│   ├── dataset/
│   │   ├── sales_train.csv                   Dữ liệu huấn luyện (2012-2022)
│   │   └── sales_test.csv                    Dữ liệu kiểm thử (2023-2024)
│   └── requirements.txt                      Thư viện Python
│
├── Nop_bai/                               Tài liệu nộp bài
│   ├── NeurIPS_Report.tex                    Báo cáo kỹ thuật (NeurIPS template)
│   ├── NeurIPS_Report.pdf                    Bản PDF đã compile
│   ├── submission_v55_m128.csv               Best submission (RMSE=740,764)
│   ├── Images/                               35+ biểu đồ EDA và SHAP
│   └── Bao_Cao_*.md/pdf                      Báo cáo chiến lược toàn diện
│
├── Analysis/                              Scripts phân tích EDA (25+ scripts)
├── baseline.ipynb                         Notebook khám phá dữ liệu
├── sample_submission.csv                  Template submission từ đề thi
└── README.md                              File này
```

---

## SHAP — Giải Thích Mô Hình

Top 5 features quan trọng nhất (SHAP TreeExplainer):

| Rank | Feature | Ý nghĩa |
|:----:|---------|---------|
| 1 | `rev_doy_mean` | Trung bình doanh thu lịch sử theo ngày trong năm |
| 2 | `time_idx` | Xu hướng tuyến tính (đếm ngày từ đầu train) |
| 3 | `rev_lag_avg` | Trung bình lag 365 và 730 ngày |
| 4 | `rev_lag_365` | Doanh thu cùng ngày năm trước |
| 5 | `rev_woy_mean` | Trung bình doanh thu theo tuần trong năm |

---

## Tài Liệu Tham Khảo

1. Ke, G., et al. "LightGBM: A Highly Efficient Gradient Boosting Decision Tree." *NeurIPS*, 2017.
2. Chen, T. & Guestrin, C. "XGBoost: A Scalable Tree Boosting System." *KDD*, 2016.
3. Prokhorenkova, L., et al. "CatBoost: Unbiased Boosting with Categorical Features." *NeurIPS*, 2018.
4. Lundberg, S. M. & Lee, S.-I. "A Unified Approach to Interpreting Model Predictions (SHAP)." *NeurIPS*, 2017.
5. VinTelligence. "Đề thi Datathon 2026 — Vòng 1." 2026.
