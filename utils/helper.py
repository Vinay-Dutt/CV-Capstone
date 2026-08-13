import os
import uuid
import time
import numpy as np
import cv2
from PIL import Image, ImageDraw
import config

def allowed_file(filename):
    """Check if the filename has a supported extension."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in config.ALLOWED_EXTENSIONS

def generate_unique_id(prefix="ICI"):
    """Generate a unique timestamped ID for analysis or comparison."""
    timestamp = int(time.time() * 1000)
    random_str = uuid.uuid4().hex[:6]
    return f"{prefix}_{timestamp}_{random_str}"

def format_file_size(size_in_bytes):
    """Format file size into human-readable string."""
    if size_in_bytes is None:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} TB"

def generate_sample_images():
    """Generates 3 synthetic sample images of varying complexity if not present."""
    samples_dir = config.STATIC_SAMPLES_FOLDER
    os.makedirs(samples_dir, exist_ok=True)
    
    sample_files = {
        'low_complexity.png': 'low',
        'medium_complexity.png': 'medium',
        'high_complexity.png': 'high'
    }
    
    generated = []
    
    for filename, level in sample_files.items():
        filepath = os.path.join(samples_dir, filename)
        if not os.path.exists(filepath):
            img = Image.new('RGB', (600, 600), color=(240, 245, 250))
            draw = ImageDraw.Draw(img)
            
            if level == 'low':
                # Simple geometric shapes, smooth background
                draw.rectangle([150, 150, 450, 450], fill=(70, 130, 180), outline=(20, 50, 100), width=4)
                draw.ellipse([220, 220, 380, 380], fill=(240, 200, 80), outline=(150, 100, 20), width=3)
                
            elif level == 'medium':
                # Multiple shapes, gradients, lines
                for i in range(12):
                    x0 = 40 + i * 45
                    y0 = 60 + (i % 3) * 150
                    draw.rectangle([x0, y0, x0 + 35, y0 + 120], fill=(30 + i*18, 100 + i*10, 200 - i*12))
                    draw.line([0, i*50, 600, 600 - i*40], fill=(200, 50, 50), width=2)
                draw.polygon([(300, 100), (500, 400), (100, 400)], outline=(0, 150, 0), width=5)
                
            elif level == 'high':
                # High texture density, noise grid, complex fractal-like structure
                np_img = np.zeros((600, 600, 3), dtype=np.uint8)
                # Grid pattern
                for y in range(0, 600, 20):
                    for x in range(0, 600, 20):
                        val = int(127 + 127 * np.sin(x/15.0) * np.cos(y/15.0))
                        np_img[y:y+20, x:x+20] = [val, (val*3)%255, (255-val)]
                # Random noise overlay
                noise = np.random.randint(0, 80, (600, 600, 3), dtype=np.uint8)
                np_img = cv2.add(np_img, noise)
                # Random circles
                for _ in range(40):
                    cx, cy = np.random.randint(50, 550, size=2)
                    r = np.random.randint(10, 50)
                    color = tuple(int(c) for c in np.random.randint(0, 255, size=3))
                    cv2.circle(np_img, (cx, cy), r, color, np.random.choice([1, 2, -1]))
                img = Image.fromarray(np_img)
                
            img.save(filepath)
        generated.append(filepath)
            
    return generated
