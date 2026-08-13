-- Schema for Image Complexity Index Generator Database

CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    original_filepath TEXT NOT NULL,
    processed_filepath TEXT NOT NULL,
    edge_filepath TEXT NOT NULL,
    contour_filepath TEXT NOT NULL,
    graph_filepath TEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_width INTEGER,
    image_height INTEGER,
    file_size_bytes INTEGER,
    
    -- Extracted Features
    edge_density REAL,
    contour_count INTEGER,
    contour_area_ratio REAL,
    glcm_contrast REAL,
    glcm_correlation REAL,
    glcm_energy REAL,
    glcm_homogeneity REAL,
    shannon_entropy REAL,
    intensity_mean REAL,
    intensity_variance REAL,
    intensity_std_dev REAL,
    
    -- Calculated Index & Rating
    ici_score REAL NOT NULL,
    complexity_level TEXT NOT NULL,
    processing_time_ms REAL,
    report_pdf_path TEXT,
    report_csv_path TEXT,
    report_excel_path TEXT
);

CREATE TABLE IF NOT EXISTS comparisons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comparison_id TEXT UNIQUE NOT NULL,
    comparison_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_count INTEGER NOT NULL,
    highest_complexity_image TEXT,
    lowest_complexity_image TEXT,
    analysis_ids_json TEXT NOT NULL
);
