# Phân tích Bão Nhiệt đới Khu vực Việt Nam — IBTrACS v4

Dự án thu thập, tiền xử lý và phân tích quỹ đạo, cường độ bão nhiệt đới ảnh hưởng đến Việt Nam giai đoạn **2000–2025**, sử dụng bộ dữ liệu **IBTrACS v4** phân phối qua HDX (Humanitarian Data Exchange).

**Môn học**: DS108 – Tiền xử lý và xây dựng bộ dữ liệu  
**Trường**: Đại học Công nghệ Thông tin – ĐHQG TP. Hồ Chí Minh  
**Nhóm thực hiện**: Vũ Minh Thư (24521733) · Đào Nguyễn Minh Thư (24521723)  
**GVHD**: TS. Nguyễn Gia Tuấn Anh · CN. Trần Quốc Khánh

---

## Mục lục

1. [Cấu trúc thư mục](#1-cấu-trúc-thư-mục)
2. [Yêu cầu môi trường](#2-yêu-cầu-môi-trường)
3. [Hướng dẫn chạy](#3-hướng-dẫn-chạy)
4. [Pipeline tổng thể](#4-pipeline-tổng-thể)
5. [Lưu ý kỹ thuật](#5-lưu-ý-kỹ-thuật)

---

## 1. Cấu trúc thư mục

```
project_root/
│
├── data/
│   ├── raw/
│   │   └── ibtracs_all_list_v04r01_vnm.csv   ← Dữ liệu gốc tải từ HDX
│   ├── processed/
│   │   ├── 01_initial_cleaned.csv            ← Output notebook 02
│   │   ├── 02_missing_handled.csv            ← Output notebook 03
│   │   └── 03_outlier_cleaned.csv            ← Output notebook 04
│   └── final_data/
│       └── final_dataset.csv                 ← Output notebook 05 (dùng cho 06–08)
│
├── notebooks/
│   ├── 01_EDA_raw.ipynb
│   ├── 02_Load_and_Initial_Cleanning.ipynb
│   ├── 03_Missing_Value.ipynb
│   ├── 04_Outlier.ipynb
│   ├── 05_Feature_Engineering.ipynb
│   ├── 06_EDA_Processed.ipynb
│   ├── 07_Intensity_Analysis.ipynb
│   └── 08_Track_Map.ipynb
│
├── output/
│   └── 08_track_globe.html                   ← Bản đồ quỹ đạo 3D tương tác (output notebook 08)
├── requirements.txt
└── README.md
```

> **Quan trọng:** Tất cả notebook đều dùng `os.chdir('..')` ở đầu để chuyển working directory về `project_root/`. Phải đặt notebook trong `notebooks/` và dữ liệu trong `data/` đúng cấu trúc trên.

---

## 2. Yêu cầu môi trường

**Python ≥ 3.9**

```bash
pip install -r requirements.txt
```

---

## 3. Hướng dẫn chạy

Cấu trúc thư mục và dữ liệu thô đã được cung cấp sẵn, không cần thiết lập thêm.

1. `01_EDA_raw.ipynb` có thể chạy ngay — chỉ cần dữ liệu thô, không phụ thuộc bước nào.

2. Mở Jupyter Notebook hoặc JupyterLab, chạy các notebook **theo đúng thứ tự** — mỗi notebook đọc output của notebook trước:

```
02 → 03 → 04 → 05
```

3. Sau khi có `final_dataset.csv`, các notebook phân tích có thể chạy theo bất kỳ thứ tự nào:

```
06, 07, 08
```

Với mỗi notebook: chạy toàn bộ các cell từ đầu đến cuối (Jupyter: **Kernel > Restart & Run All** / VS Code: **Run All** / Colab: **Runtime > Run all**).

---

## 4. Pipeline tổng thể

```
ibtracs_all_list_v04r01_vnm.csv
(~1870–T2/2026 | 227,142 dòng × 10 cột | 20.52 MB)
           │
           ▼  [02] Load & Initial Cleaning
           │  • Parse ISO_TIME, lọc 2000–2025
           │  • Kiểm tra invalid values, loại duplicate
           ▼
   01_initial_cleaned.csv
           │
           ▼  [03] Missing Value Handling
           │  • PCHIP (gap ≤21h) / Linear (24–45h) / NaN (>45h)
           │  • Bảo toàn cấu trúc track, không tạo giá trị phi vật lý
           ▼
   02_missing_handled.csv
           │
           ▼  [04] Outlier Detection & Treatment
           │  • Intrinsic (RI/RW, W-P nhẹ) → giữ nguyên
           │  • Extrinsic (spike, W-P nặng) → cap
           │  • Translation speed > 60kt → drop (9 điểm)
           ▼
   03_outlier_cleaned.csv
           │
           ▼  [05] Feature Engineering
           │  • SEASON, INTENSITY_CAT_FINAL, HAS_INTENSITY
           │  • CAT_CONFLICT, PEAK_CAT_FINAL, ...
           ▼
   final_dataset.csv
   (40,838 dòng × 20 cột | 719 cơn bão | 2000–2025)
           │
     ┌─────┼──────────┐
     ▼     ▼          ▼
  [06]   [07]       [08]
  EDA   Intensity  Track Map
        Analysis   (Cartopy +
        (STL,       KDE Heatmap)
        Mann-Kendall)
```

---

## 5. Lưu ý kỹ thuật

**Dữ liệu năm 2025 thiếu hoàn toàn WMO_WIND/WMO_PRES:**  
Do JMA chưa phát hành best track chính thức cho năm 2025 tại thời điểm tải dữ liệu. Notebook 07 tự động loại năm 2025 khỏi phân tích cường độ thông qua cột `HAS_INTENSITY`.
