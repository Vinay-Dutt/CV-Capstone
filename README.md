# Image Complexity Index Generator for Digital Image Complexity Assessment

> **A Production-Quality Classical Computer Vision Capstone Web Application**

---

## 📌 Project Overview

The **Image Complexity Index (ICI) Generator** is a production-quality, responsive web application designed for assessing, quantifying, and ranking digital image complexity using **classical Computer Vision and Image Processing algorithms**. 

Unlike deep learning approaches which operate as opaque black boxes, this system relies entirely on deterministic mathematical and structural metrics: **Canny Edge Density**, **Contour Topology**, **Gray-Level Co-occurrence Matrix (GLCM) Texture Analysis**, **Shannon Information Entropy**, and **Intensity Variance Moments**.

---

## 🚀 Key Features

- **Single & Multi-Image Upload**: Drag-and-drop support for JPG, JPEG, PNG, BMP, and TIFF formats.
- **Classical CV Preprocessing**: Resizing with aspect-ratio preservation, RGB to Grayscale conversion, Median noise reduction, Gaussian smoothing, and Adaptive CLAHE Histogram Equalization.
- **Visual Feature Extraction**:
  - *Structural*: Canny Edge Density, Contour Count, Contour Area Ratio.
  - *Textural*: GLCM Contrast, Correlation, Energy, Homogeneity.
  - *Informational*: Shannon Entropy ($H = -\sum p_i \log_2 p_i$).
  - *Statistical*: Pixel Intensity Mean, Variance, Standard Deviation, Skewness.
- **Weighted Mathematical ICI Scoring**: Fuses extracted component metrics into a normalized 0–100 Image Complexity Index classified into 5 standard levels (**Very Low**, **Low**, **Medium**, **High**, **Very High**).
- **Interactive Visualizations**: Dynamic Chart.js Radar Charts, Sub-Domain Breakdown Bar Charts, Pixel Intensity Histograms, and circular ICI Meter Gauges.
- **Multi-Image Comparison & Ranking**: Ranks image batches side-by-side and highlights extrema (Highest vs Lowest complexity images).
- **SQLite Processing History**: Persistent storage of past image analyses with search, filter, view, and record management.
- **Automated Multi-Format Reporting**: Export assessment reports in **PDF**, **Excel (.xlsx)**, and **CSV** formats.
- **SaaS Glassmorphism Dashboard UI**: Bootstrap 5 dark and light mode responsive themes with micro-interactions and smooth animations.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | HTML5, CSS3 (Glassmorphism), JavaScript (ES6+), Bootstrap 5, Chart.js 4, Font Awesome 6 |
| **Backend** | Python 3.10+, Flask 3.0, Werkzeug |
| **CV & Math Libraries** | OpenCV (`opencv-python-headless`), NumPy, Scikit-Image, SciPy, Pillow, Pandas |
| **Reporting & DB** | SQLite3, ReportLab (PDF), OpenPyXL (Excel), Matplotlib (`Agg` backend) |

---

## 📁 Project Directory Structure

```
ImageComplexityIndexGenerator/
├── app.py                      # Core Flask web server & REST API controller
├── config.py                   # Global constants, paths, thresholds, and weights
├── requirements.txt            # Python package dependencies
├── schema.sql                  # SQLite database table definitions
├── README.md                   # Complete technical documentation
├── modules/
│   ├── preprocessing.py        # Resizing, grayscale, gaussian blur, CLAHE equalization
│   ├── feature_extraction.py   # Canny edges, contours, GLCM matrix, Shannon entropy
│   ├── complexity_score.py     # ICI mathematical scoring formula & classification
│   ├── visualization.py        # Matplotlib radar, bar, & histogram figure generator
│   ├── comparison.py           # Multi-image ranking & extrema identification engine
│   └── report_generator.py     # PDF (ReportLab), Excel (OpenPyXL), & CSV exporter
├── utils/
│   ├── database.py             # SQLite CRUD operations & history management
│   └── helper.py               # Validation, unique ID, formatting, & sample generators
├── static/
│   ├── css/
│   │   ├── style.css           # Glassmorphism design system & light/dark tokens
│   │   └── dashboard.css       # Dropzones, gauges, preview cards, & table styling
│   ├── js/
│   │   ├── main.js            # Theme switcher, toasts, & sidebar responsiveness
│   │   ├── charts.js          # Chart.js radar, bar, gauge, & pie renderers
│   │   └── upload.js          # Drag & drop upload, AJAX submission, & progress bar
│   └── images/
│       └── samples/            # Generated synthetic sample demo images
└── templates/
    ├── base.html               # Main layout template with sidebar & navbar
    ├── index.html              # Landing home page with project stats & CTA
    ├── dashboard.html          # Comprehensive analysis workspace & layer views
    ├── upload.html             # Drag & drop uploader with hyperparameter tuning
    ├── comparison.html         # Multi-image comparison matrix & ranking
    ├── history.html            # SQLite persistent history log table
    ├── reports.html            # Report export center
    ├── about.html              # Theoretical methodology & mathematical formulas
    └── help.html               # Step-by-step operating guide & FAQ
```

---

## 💻 Installation & Execution Instructions

### 1. Prerequisites
- Python 3.9 or higher installed.

### 2. Install Dependencies
Open your terminal/command prompt in the project root directory and run:

```bash
pip install -r requirements.txt
```

### 3. Run Application
Start the Flask dev server by executing:

```bash
python app.py
```

### 4. Access Web Interface
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔬 Mathematical Formulations

### 1. Canny Edge Density ($D_{\text{edge}}$)
$$D_{\text{edge}} = \frac{\sum_{x,y} E(x,y)}{W \times H}$$
Where $E(x,y) \in \{0, 1\}$ represents binary Canny edge pixels and $W \times H$ is the image resolution.

### 2. Shannon Information Entropy ($H$)
$$H = -\sum_{i=0}^{255} p(i) \log_2 p(i)$$
Where $p(i)$ is the normalized frequency of pixel gray level $i$.

### 3. Image Complexity Index (ICI) Formula
$$\text{ICI} = \sum_{k=1}^{6} w_k \cdot \hat{S}_k$$
Where $\hat{S}_k \in [0, 100]$ are non-linearly normalized feature sub-scores and $\sum w_k = 1.0$.

---

## 🏆 Capstone Project Verification Checklist

- [x] Classical CV techniques only (No ML/DL).
- [x] Flask MVC architecture with separate modules.
- [x] Complete SQLite database implementation.
- [x] Interactive Chart.js visualizers & Matplotlib graphs.
- [x] Downloadable PDF, CSV, and Excel assessment reports.
- [x] Modern SaaS UI with Light/Dark Mode toggle.
