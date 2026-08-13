import os
import time
import json
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename

import config
from utils.database import (
    init_db, save_analysis, get_all_analyses, get_analysis_by_id,
    delete_analysis_by_id, save_comparison, get_db_stats, update_analysis_report_paths,
    get_comparison_by_id, get_latest_comparison, get_db_connection
)
from utils.helper import allowed_file, generate_unique_id, generate_sample_images
from modules.preprocessing import ImagePreprocessor
from modules.feature_extraction import FeatureExtractor
from modules.complexity_score import ComplexityScorer
from modules.visualization import Visualizer
from modules.comparison import ImageComparer
from modules.report_generator import ReportGenerator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ICI_CapStone_Secret_Key_2026_Vision_System'
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Initialize SQLite database & synthetic sample images on startup
init_db()
generate_sample_images()

# Instantiate Core CV Engines
preprocessor = ImagePreprocessor()
extractor = FeatureExtractor()
scorer = ComplexityScorer()
visualizer = Visualizer()
comparer = ImageComparer()
reporter = ReportGenerator()


# =========================================================================
# WEB ROUTE HANDLERS
# =========================================================================

@app.route('/')
def index():
    """Home Page with hero banner, statistics cards, and recent history."""
    stats = get_db_stats()
    recent = get_all_analyses(limit=5)
    return render_template('index.html', stats=stats, recent_analyses=recent)


@app.route('/dashboard')
def dashboard_page():
    """Main Assessment Dashboard view for inspecting a specific analysis record."""
    analysis_id = request.args.get('id')
    analysis_data = None
    score_result = None
    
    if analysis_id:
        analysis_data = get_analysis_by_id(analysis_id)
        if analysis_data:
            # Reconstruct score sub-breakdown for dashboard charts
            score_result = scorer.compute_ici(analysis_data)
    else:
        # Load most recent analysis if available
        recent = get_all_analyses(limit=1)
        if recent:
            analysis_data = recent[0]
            score_result = scorer.compute_ici(analysis_data)

    return render_template('dashboard.html', analysis=analysis_data, score_result=score_result)


@app.route('/upload')
def upload_page():
    """Upload Page for drag & drop single or batch image processing."""
    return render_template('upload.html')


@app.route('/comparison')
def comparison_page():
    """Multi-Image Comparison & Ranking matrix page."""
    comparison_id = request.args.get('id')
    comp_row = None
    
    if comparison_id:
        comp_row = get_comparison_by_id(comparison_id)
    else:
        comp_row = get_latest_comparison()
        
    comparison_data = None
    if comp_row:
        try:
            analysis_ids = json.loads(comp_row['analysis_ids_json'])
            ranked_items = []
            for aid in analysis_ids:
                item_data = None
                if isinstance(aid, int):
                    conn = get_db_connection()
                    cur = conn.cursor()
                    cur.execute("SELECT * FROM analyses WHERE id = ?", (aid,))
                    row = cur.fetchone()
                    conn.close()
                    item_data = dict(row) if row else None
                else:
                    item_data = get_analysis_by_id(str(aid))
                    
                if item_data:
                    item_dict = dict(item_data)
                    item_dict['filepath'] = item_dict['original_filepath']
                    score_info = scorer.classify_complexity(item_dict['ici_score'])
                    item_dict['color_hex'] = score_info['color']
                    item_dict['badge_class'] = score_info['badge']
                    item_dict['features'] = item_dict
                    ranked_items.append(item_dict)
                    
            ranked_items.sort(key=lambda x: x['ici_score'], reverse=True)
            for idx, item in enumerate(ranked_items, start=1):
                item['rank'] = idx
                
            if ranked_items:
                highest = ranked_items[0]
                lowest = ranked_items[-1]
                graph_path = comparer.generate_comparison_chart(ranked_items)
                comparison_data = {
                    'count': len(ranked_items),
                    'ranked_images': ranked_items,
                    'highest_complexity': highest,
                    'lowest_complexity': lowest,
                    'comparison_graph_filepath': graph_path
                }
        except Exception as e:
            comparison_data = None
            
    return render_template('comparison.html', comparison=comparison_data)


@app.route('/history')
def history_page():
    """Processing History log page listing all SQLite entries."""
    history = get_all_analyses(limit=100)
    return render_template('history.html', history=history)


@app.route('/reports')
def reports_page():
    """Report Generation & Export center page."""
    recent = get_all_analyses(limit=20)
    return render_template('reports.html', recent_analyses=recent)


@app.route('/about')
def about_page():
    """Theoretical methodology and mathematical formulas page."""
    return render_template('about.html')


@app.route('/help')
def help_page():
    """User guide & troubleshooting FAQ page."""
    return render_template('help.html')


@app.route('/sample-demo')
def run_sample_demo():
    """Quick trigger to automatically run complexity assessment on a pre-loaded synthetic image."""
    samples_dir = config.STATIC_SAMPLES_FOLDER
    sample_file = os.path.join(samples_dir, 'medium_complexity.png')
    
    if not os.path.exists(sample_file):
        generate_sample_images()
        
    analysis_id = run_single_analysis(sample_file, "medium_complexity.png")
    return redirect(url_for('dashboard_page', id=analysis_id))


# =========================================================================
# REST API ENDPOINTS
# =========================================================================

@app.route('/api/analyze', methods=['POST'])
def api_analyze_single():
    """
    POST API Endpoint for processing a single image upload.
    Returns JSON response with analysis_id and complexity score.
    """
    if 'image' not in request.files and 'images' not in request.files:
        return jsonify({'error': 'No image file provided in request.'}), 400
        
    file = request.files.get('image') or request.files.get('images')
    if not file or file.filename == '':
        return jsonify({'error': 'Selected file is empty or invalid.'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file format. Allowed: JPG, PNG, BMP, TIFF.'}), 400

    try:
        # Save raw uploaded file safely
        filename = secure_filename(file.filename)
        unique_prefix = generate_unique_id("IMG")
        upload_filename = f"{unique_prefix}_{filename}"
        upload_filepath = os.path.join(config.UPLOAD_FOLDER, upload_filename)
        file.save(upload_filepath)

        # Extract hyperparameter options from form
        gaussian_k = request.form.get('gaussian_kernel', 5)
        canny_l = request.form.get('canny_low', 50)
        canny_h = request.form.get('canny_high', 150)

        # Run analysis pipeline
        analysis_id = run_single_analysis(
            upload_filepath, filename, unique_prefix=unique_prefix,
            gaussian_kernel=gaussian_k, canny_low=canny_l, canny_high=canny_h
        )
        return jsonify({'success': True, 'analysis_id': analysis_id})

    except Exception as e:
        return jsonify({'error': f"Processing error: {str(e)}"}), 500


@app.route('/api/compare', methods=['POST'])
def api_compare_batch():
    """
    POST API Endpoint for processing multiple images in a batch.
    Ranks images and produces extrema highlights.
    """
    files = request.files.getlist('images')
    if not files or len(files) < 2:
        return jsonify({'error': 'Please select at least 2 images for comparison.'}), 400

    saved_paths = []
    try:
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_prefix = generate_unique_id("COMP_IMG")
                upload_filename = f"{unique_prefix}_{filename}"
                upload_filepath = os.path.join(config.UPLOAD_FOLDER, upload_filename)
                file.save(upload_filepath)
                saved_paths.append(upload_filepath)

        comp_result = comparer.compare_images(saved_paths)
        comp_id = generate_unique_id("COMP")
        
        # Save analysis records for each image into SQLite database
        analysis_ids = []
        for item in comp_result['ranked_images']:
            data_to_save = {
                'analysis_id': generate_unique_id("ICI"),
                'filename': item['filename'],
                'original_filepath': item['filepath'],
                'processed_filepath': item['processed_filepath'],
                'edge_filepath': item['edge_filepath'],
                'contour_filepath': item['edge_filepath'], # fallback contour path
                'graph_filepath': comp_result['comparison_graph_filepath'],
                'image_width': item['width'],
                'image_height': item['height'],
                'file_size_bytes': item['file_size'],
                'edge_density': item['features']['edge_density'],
                'contour_count': item['features']['contour_count'],
                'contour_area_ratio': item['features']['contour_area_ratio'],
                'glcm_contrast': item['features']['glcm_contrast'],
                'glcm_correlation': item['features']['glcm_correlation'],
                'glcm_energy': item['features']['glcm_energy'],
                'glcm_homogeneity': item['features']['glcm_homogeneity'],
                'shannon_entropy': item['features']['shannon_entropy'],
                'intensity_mean': item['features']['intensity_mean'],
                'intensity_variance': item['features']['intensity_variance'],
                'intensity_std_dev': item['features']['intensity_std_dev'],
                'ici_score': item['ici_score'],
                'complexity_level': item['complexity_level'],
                'processing_time_ms': 150.0
            }
            inserted_id = save_analysis(data_to_save)
            analysis_ids.append(data_to_save['analysis_id'])

        save_comparison(
            comp_id, "Multi-Image Assessment", comp_result['count'],
            comp_result['highest_complexity']['filename'],
            comp_result['lowest_complexity']['filename'],
            analysis_ids
        )

        return jsonify({'success': True, 'comparison_id': comp_id})

    except Exception as e:
        return jsonify({'error': f"Batch comparison failed: {str(e)}"}), 500


@app.route('/api/history/<analysis_id>', methods=['DELETE'])
def api_delete_history(analysis_id):
    """DELETE Endpoint to remove an analysis record from SQLite."""
    success = delete_analysis_by_id(analysis_id)
    if success:
        return jsonify({'success': True})
    return jsonify({'error': 'Record not found.'}), 404


@app.route('/api/export/<format_type>/<analysis_id>')
def export_report(format_type, analysis_id):
    """Download generated PDF, CSV, or Excel report files (Single, Latest, or Bulk Dataset)."""
    if analysis_id == 'latest':
        recent = get_all_analyses(limit=1)
        if recent:
            data = recent[0]
        else:
            # Generate sample image demo if database is currently empty
            samples_dir = config.STATIC_SAMPLES_FOLDER
            sample_file = os.path.join(samples_dir, 'medium_complexity.png')
            if not os.path.exists(sample_file):
                generate_sample_images()
            latest_id = run_single_analysis(sample_file, "sample_demo.png")
            data = get_analysis_by_id(latest_id)
        analysis_id = data['analysis_id']
    elif analysis_id == 'bulk':
        all_data = get_all_analyses(limit=500)
        if not all_data:
            samples_dir = config.STATIC_SAMPLES_FOLDER
            sample_file = os.path.join(samples_dir, 'medium_complexity.png')
            if not os.path.exists(sample_file):
                generate_sample_images()
            latest_id = run_single_analysis(sample_file, "sample_demo.png")
            all_data = get_all_analyses(limit=500)
            
        if format_type == 'excel':
            filepath = reporter.export_bulk_excel(all_data, filename_prefix="bulk_dataset_report")
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            filepath = reporter.export_bulk_csv(all_data, filename_prefix="bulk_dataset_report")
            mimetype = 'text/csv'
            
        return send_file(filepath, mimetype=mimetype, as_attachment=True)
    else:
        data = get_analysis_by_id(analysis_id)

    if not data:
        return "Analysis record not found", 404

    prefix = f"report_{analysis_id}"
    
    if format_type == 'pdf':
        filepath = reporter.export_pdf(data, filename_prefix=prefix)
        mimetype = 'application/pdf'
    elif format_type == 'excel':
        filepath = reporter.export_excel(data, filename_prefix=prefix)
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif format_type == 'csv':
        filepath = reporter.export_csv(data, filename_prefix=prefix)
        mimetype = 'text/csv'
    else:
        return "Invalid export format specified", 400

    return send_file(filepath, mimetype=mimetype, as_attachment=True)


@app.route('/files/<path:filename>')
def serve_file(filename):
    """Helper route to securely serve image and graph artifacts."""
    if os.path.isabs(filename) and os.path.exists(filename):
        return send_file(filename)
    return "File not found", 404


# =========================================================================
# HELPER PIPELINE METHOD
# =========================================================================

def run_single_analysis(image_path, original_filename, unique_prefix=None, gaussian_kernel=5, canny_low=50, canny_high=150):
    """Executes the full pipeline for a single image and stores to database."""
    start_time = time.time()
    if not unique_prefix:
        unique_prefix = generate_unique_id("IMG")
        
    analysis_id = generate_unique_id("ICI")
    
    # 1. Preprocessing
    prep_data = preprocessor.process_pipeline(image_path, filename_prefix=unique_prefix)
    gray = prep_data['grayscale']
    
    # 2. Visual Feature Extraction with custom Canny thresholds
    custom_extractor = FeatureExtractor(
        low_threshold=int(canny_low) if str(canny_low).isdigit() else 50,
        high_threshold=int(canny_high) if str(canny_high).isdigit() else 150
    )
    features = custom_extractor.extract_all_features(gray, filename_prefix=unique_prefix)
    features['gray_img'] = gray
    
    # 3. Complexity Scoring Model
    score_result = scorer.compute_ici(features)
    
    # 4. Generate Dashboard Matplotlib Figure
    graph_filepath = visualizer.generate_analysis_dashboard_graph(features, score_result, filename_prefix=unique_prefix)
    
    elapsed_ms = round((time.time() - start_time) * 1000, 2)
    
    # 5. Build Database Record
    record = {
        'analysis_id': analysis_id,
        'filename': original_filename,
        'original_filepath': image_path,
        'processed_filepath': prep_data['processed_filepath'],
        'edge_filepath': features['edge_filepath'],
        'contour_filepath': features['contour_filepath'],
        'graph_filepath': graph_filepath,
        'image_width': prep_data['width'],
        'image_height': prep_data['height'],
        'file_size_bytes': prep_data['file_size'],
        'edge_density': features['edge_density'],
        'contour_count': features['contour_count'],
        'contour_area_ratio': features['contour_area_ratio'],
        'glcm_contrast': features['glcm_contrast'],
        'glcm_correlation': features['glcm_correlation'],
        'glcm_energy': features['glcm_energy'],
        'glcm_homogeneity': features['glcm_homogeneity'],
        'shannon_entropy': features['shannon_entropy'],
        'intensity_mean': features['intensity_mean'],
        'intensity_variance': features['intensity_variance'],
        'intensity_std_dev': features['intensity_std_dev'],
        'ici_score': score_result['ici_score'],
        'complexity_level': score_result['complexity_level'],
        'processing_time_ms': elapsed_ms
    }
    
    # Generate default PDF, CSV, Excel report files
    report_prefix = f"report_{analysis_id}"
    pdf_p = reporter.export_pdf(record, filename_prefix=report_prefix)
    csv_p = reporter.export_csv(record, filename_prefix=report_prefix)
    excel_p = reporter.export_excel(record, filename_prefix=report_prefix)
    
    record['report_pdf_path'] = pdf_p
    record['report_csv_path'] = csv_p
    record['report_excel_path'] = excel_p
    
    save_analysis(record)
    return analysis_id


# =========================================================================
# APPLICATION ENTRYPOINT
# =========================================================================

if __name__ == '__main__':
    print("==================================================================")
    print(" Image Complexity Index (ICI) Generator Web Server Launching...")
    print(" Classical Computer Vision Capstone Engine Active")
    print(" Access Web UI at: http://127.0.0.1:5000")
    print("==================================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
