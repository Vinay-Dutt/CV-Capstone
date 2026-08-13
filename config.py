import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Data directory configuration (defaults to project base directory)
DATA_DIR = os.environ.get('DATA_DIR', BASE_DIR)

# Folder Directories
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(DATA_DIR, 'uploads'))
OUTPUT_FOLDER = os.environ.get('OUTPUT_FOLDER', os.path.join(DATA_DIR, 'outputs'))
GRAPH_FOLDER = os.environ.get('GRAPH_FOLDER', os.path.join(DATA_DIR, 'graphs'))
REPORT_FOLDER = os.environ.get('REPORT_FOLDER', os.path.join(DATA_DIR, 'reports'))
STATIC_SAMPLES_FOLDER = os.path.join(BASE_DIR, 'static', 'images', 'samples')

DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.join(DATA_DIR, 'database.db'))
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')

# Upload constraints
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif'}

# Image Processing Defaults
DEFAULT_MAX_DIMENSION = 1024
DEFAULT_GAUSSIAN_KERNEL = (5, 5)
DEFAULT_CANNY_LOW = 50
DEFAULT_CANNY_HIGH = 150

# ICI Scoring Model Weights (Must sum to 1.0)
# Edge Density (0.25), Contour Metric (0.20), GLCM Texture (0.25), Shannon Entropy (0.20), Intensity Statistics (0.10)
ICI_FEATURE_WEIGHTS = {
    'edge_density': 0.25,
    'contour_density': 0.20,
    'glcm_contrast': 0.15,
    'glcm_entropy': 0.10,
    'shannon_entropy': 0.20,
    'intensity_variance': 0.10
}

# Standard Complexity Ranges (0 - 100)
COMPLEXITY_LEVELS = [
    {'name': 'Very Low', 'min': 0.0, 'max': 20.0, 'badge': 'bg-info', 'color': '#0dcaf0'},
    {'name': 'Low', 'min': 20.0, 'max': 40.0, 'badge': 'bg-success', 'color': '#198754'},
    {'name': 'Medium', 'min': 40.0, 'max': 60.0, 'badge': 'bg-warning', 'color': '#ffc107'},
    {'name': 'High', 'min': 60.0, 'max': 80.0, 'badge': 'bg-danger', 'color': '#dc3545'},
    {'name': 'Very High', 'min': 80.0, 'max': 100.0, 'badge': 'bg-dark', 'color': '#6c757d'}
]

# Ensure all essential directories exist on startup
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, GRAPH_FOLDER, REPORT_FOLDER, STATIC_SAMPLES_FOLDER]:
    os.makedirs(folder, exist_ok=True)
