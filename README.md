# 🏆 Datathon 2026 — The Gridbreakers (Vòng 1)

> **Dự báo Doanh thu & Giá vốn hàng bán** cho doanh nghiệp thời trang e-commerce Việt Nam.  
> Cuộc thi tổ chức bởi VinTelligence — VinUniversity DS&AI Club.

---

## ⚡ Quick Start — Tái Lập Kết Quả

```bash
cd train_model
pip install -r requirements.txt
python scripts/train_v6.py
python scripts/check_constraints.py
```

---

## 📁 Cấu Trúc Thư Mục

```
datathon-2026-round-1/
│
├── train_model/                    # 🔥 Pipeline ML chính
│   ├── scripts/
│   │   ├── train_v6.py             #   Pipeline: Feature Eng → LightGBM → SHAP
│   │   ├── check_constraints.py    #   Kiểm tra ràng buộc đề thi
│   │   └── evaluate.py             #   Đánh giá mô hình
│   ├── dataset/
│   │   ├── sales_train.csv         #   Train: 2012-2022 (3,833 ngày)
│   │   └── sales_test.csv          #   Test: 2023-2024 (548 ngày)
│   ├── model_v6/                   #   SHAP plots + metrics (model binaries excluded)
│   ├── requirements.txt            #   Thư viện pinned versions
│   ├── submission_v6.csv           #   File nộp Kaggle
│   └── README.md                   #   Chi tiết kỹ thuật
│
├── Nop_bai/                        # 📄 Tài liệu nộp bài
│   ├── NeurIPS_Report.tex          #   Báo cáo LaTeX (NeurIPS template, 4 trang)
│   ├── NeurIPS_Report.pdf          #   PDF compiled
│   ├── submission.csv              #   File nộp Kaggle (copy từ v6)
│   ├── Images/                     #   36 biểu đồ EDA + SHAP
│   └── Bao_Cao_Chien_Luoc_*.md     #   Báo cáo chiến lược đầy đủ
│
├── analysis_*.py                   # Scripts phân tích EDA
├── baseline.ipynb                  # Notebook khám phá dữ liệu
└── README.md                       # File này
```

---

## 📊 Hiệu Suất Mô Hình (v6)

| Metric | Giá trị |
|--------|:-------:|
| **R²** | 0.7978 |
| **MAE** | 531,042 |
| **MAPE** | 21.1% |

**Kiến trúc:** LightGBM Ensemble (5 seeds) + Log-transform + 40 known-in-advance features + SHAP TreeExplainer.

---

## 🔗 Links

- **Kaggle:** [datathon-2026-round-1](https://www.kaggle.com/competitions/datathon-2026-round-1)
