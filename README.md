# Datathon 2026 — Vong 1 | The Gridbreakers

**De tai:** Du bao Doanh thu va Gia von hang ban cho doanh nghiep thoi trang e-commerce Viet Nam.  
**Cuoc thi:** To chuc boi VinTelligence — VinUniversity DS&AI Club.

---

## Huong Dan Tai Lap Ket Qua

Toan bo pipeline co the duoc tai lap bang 3 dong lenh sau:

```bash
cd train_model
pip install -r requirements.txt
python scripts/train_v6.py
```

Kiem tra rang buoc de bai:

```bash
python scripts/check_constraints.py
```

---

## Cau Truc Thu Muc

```
datathon-2026-round-1/
│
├── train_model/                        Pipeline hoc may chinh
│   ├── scripts/
│   │   ├── train_v6.py                     Feature Engineering + LightGBM + SHAP
│   │   ├── check_constraints.py            Kiem tra rang buoc de thi (10 tieu chi)
│   │   └── evaluate.py                     Danh gia mo hinh tren tap validation
│   ├── dataset/
│   │   ├── sales_train.csv                 Du lieu huan luyen: 2012-2022
│   │   └── sales_test.csv                  Du lieu kiem thu: 2023-2024
│   ├── model_v6/                           SHAP plots, metrics, feature list
│   ├── requirements.txt                    Thu vien kem phien ban cu the
│   └── submission_v6.csv                   Ket qua du bao cuoi cung
│
├── Nop_bai/                            Tai lieu nop bai
│   ├── NeurIPS_Report.tex                  Bao cao ky thuat (NeurIPS template, 4 trang)
│   ├── NeurIPS_Report.pdf                  Ban PDF da compile
│   ├── submission.csv                      File nop len Kaggle
│   ├── Images/                             36 bieu do EDA va SHAP
│   └── Bao_Cao_Chien_Luoc_*.md             Bao cao chien luoc toan dien
│
├── Analysis/                           Scripts phan tich EDA
├── baseline.ipynb                      Notebook kham pha du lieu
└── README.md                           File nay
```

---

## Hieu Suat Mo Hinh

Mo hinh LightGBM Ensemble (5 seeds) duoc danh gia tren tap hold-out 18 thang (07/2021 - 12/2022):

| Chi so | Gia tri |
|--------|:-------:|
| R-squared | 0.7978 |
| MAE | 531,042 |
| RMSE | 698,857 |
| MAPE | 21.1% |

**Kien truc:** LightGBM GBDT voi log-transform, ensemble 5 random seeds, 40 dac trung "known-in-advance", ket hop SHAP TreeExplainer de giai thich ket qua du bao.

**Chong ro ri du lieu:** Toan bo dac trung chi su dung thong tin co the biet truoc tai thoi diem du bao. Bien khuyen mai bi loai bo hoan toan. Lag features chi truy xuat tu tap huan luyen.

---

## Tai Lieu Tham Khao

1. Ke, G., et al. "LightGBM: A Highly Efficient Gradient Boosting Decision Tree." NeurIPS, 2017.
2. Lundberg, S. M. & Lee, S.-I. "A Unified Approach to Interpreting Model Predictions (SHAP)." NeurIPS, 2017.
3. VinTelligence. "De thi Datathon 2026 — Vong 1." 2026.
