import sqlite3
import json
import os
import config

def get_db_connection():
    """Establish and return a SQLite database connection with row factory."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the SQLite database schema if not already initialized."""
    if not os.path.exists(config.SCHEMA_PATH):
        raise FileNotFoundError(f"Schema file not found at {config.SCHEMA_PATH}")
    
    with open(config.SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()
        
    conn = get_db_connection()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()

def save_analysis(data):
    """Save analysis record to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    INSERT INTO analyses (
        analysis_id, filename, original_filepath, processed_filepath,
        edge_filepath, contour_filepath, graph_filepath, image_width,
        image_height, file_size_bytes, edge_density, contour_count,
        contour_area_ratio, glcm_contrast, glcm_correlation, glcm_energy,
        glcm_homogeneity, shannon_entropy, intensity_mean, intensity_variance,
        intensity_std_dev, ici_score, complexity_level, processing_time_ms,
        report_pdf_path, report_csv_path, report_excel_path
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        data.get('analysis_id'),
        data.get('filename'),
        data.get('original_filepath'),
        data.get('processed_filepath'),
        data.get('edge_filepath'),
        data.get('contour_filepath'),
        data.get('graph_filepath'),
        data.get('image_width'),
        data.get('image_height'),
        data.get('file_size_bytes'),
        data.get('edge_density'),
        data.get('contour_count'),
        data.get('contour_area_ratio'),
        data.get('glcm_contrast'),
        data.get('glcm_correlation'),
        data.get('glcm_energy'),
        data.get('glcm_homogeneity'),
        data.get('shannon_entropy'),
        data.get('intensity_mean'),
        data.get('intensity_variance'),
        data.get('intensity_std_dev'),
        data.get('ici_score'),
        data.get('complexity_level'),
        data.get('processing_time_ms'),
        data.get('report_pdf_path'),
        data.get('report_csv_path'),
        data.get('report_excel_path')
    )
    
    cursor.execute(query, params)
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def get_all_analyses(limit=100):
    """Retrieve all analysis records sorted by date descending."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses ORDER BY upload_date DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_analysis_by_id(analysis_id):
    """Retrieve a single analysis record by analysis_id string."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses WHERE analysis_id = ?", (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_analysis_by_id(analysis_id):
    """Delete an analysis record from database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analyses WHERE analysis_id = ?", (analysis_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def update_analysis_report_paths(analysis_id, pdf_path, csv_path, excel_path):
    """Update report file paths for an existing analysis record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE analyses 
        SET report_pdf_path = ?, report_csv_path = ?, report_excel_path = ?
        WHERE analysis_id = ?
    """, (pdf_path, csv_path, excel_path, analysis_id))
    conn.commit()
    conn.close()

def save_comparison(comparison_id, name, count, highest_img, lowest_img, analysis_ids):
    """Save a multi-image comparison record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO comparisons (
        comparison_id, comparison_name, image_count, highest_complexity_image,
        lowest_complexity_image, analysis_ids_json
    ) VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (
        comparison_id, name, count, highest_img, lowest_img, json.dumps(analysis_ids)
    ))
    conn.commit()
    conn.close()

def get_comparison_by_id(comparison_id):
    """Retrieve comparison record by comparison_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comparisons WHERE comparison_id = ?", (comparison_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_latest_comparison():
    """Retrieve the most recent comparison record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comparisons ORDER BY created_at DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_db_stats():
    """Get database statistics for summary dashboard cards."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM analyses")
    total_images = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(ici_score) FROM analyses")
    avg_ici_res = cursor.fetchone()[0]
    avg_ici = round(avg_ici_res, 2) if avg_ici_res else 0.0
    
    cursor.execute("SELECT COUNT(*) FROM comparisons")
    total_comparisons = cursor.fetchone()[0]
    
    # Distribution by complexity level
    cursor.execute("""
        SELECT complexity_level, COUNT(*) as count 
        FROM analyses 
        GROUP BY complexity_level
    """)
    dist_rows = cursor.fetchall()
    distribution = {row['complexity_level']: row['count'] for row in dist_rows}
    
    conn.close()
    return {
        'total_images': total_images,
        'avg_ici': avg_ici,
        'total_comparisons': total_comparisons,
        'distribution': distribution
    }
