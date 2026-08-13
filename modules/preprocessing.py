import os
import cv2
import numpy as np
from PIL import Image
import config

class ImagePreprocessor:
    """
    Classical Image Processing module to clean, normalize, and prepare images for feature extraction.
    """
    
    def __init__(self, max_dim=config.DEFAULT_MAX_DIMENSION):
        self.max_dim = max_dim

    def load_image(self, image_path):
        """
        Safely load image from disk supporting non-ASCII paths and various formats.
        Returns BGR numpy image array.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at path: {image_path}")
            
        try:
            # Using Pillow to avoid OpenCV path issues with special characters
            pil_img = Image.open(image_path)
            pil_img = pil_img.convert('RGB')
            # Convert RGB PIL to BGR OpenCV format
            rgb_arr = np.array(pil_img)
            bgr_arr = cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2BGR)
            return bgr_arr
        except Exception as e:
            raise ValueError(f"Failed to load or parse image: {str(e)}")

    def resize_aspect_ratio(self, img):
        """
        Resizes the image such that the maximum dimension does not exceed max_dim,
        preserving aspect ratio.
        """
        h, w = img.shape[:2]
        if max(h, w) <= self.max_dim:
            return img
            
        if h > w:
            new_h = self.max_dim
            new_w = int(w * (self.max_dim / float(h)))
        else:
            new_w = self.max_dim
            new_h = int(h * (self.max_dim / float(w)))
            
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return resized

    def to_grayscale(self, img_bgr):
        """Convert BGR image to single-channel Grayscale."""
        if len(img_bgr.shape) == 2:
            return img_bgr
        return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    def apply_gaussian_blur(self, gray_img, kernel_size=config.DEFAULT_GAUSSIAN_KERNEL, sigma=1.0):
        """Apply Gaussian Blur to smooth noise while preserving significant boundaries."""
        if isinstance(kernel_size, (int, float, str)):
            try:
                k = int(kernel_size)
                if k % 2 == 0:
                    k += 1
                kernel_size = (k, k)
            except Exception:
                kernel_size = (5, 5)
        return cv2.GaussianBlur(gray_img, kernel_size, sigmaX=sigma, sigmaY=sigma)

    def apply_histogram_equalization(self, gray_img):
        """Apply Contrast Limited Adaptive Histogram Equalization (CLAHE) for robust contrast enhancement."""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray_img)

    def reduce_noise(self, gray_img, ksize=3):
        """Apply Median Filter for salt-and-pepper noise reduction."""
        return cv2.medianBlur(gray_img, ksize)

    def normalize_image(self, gray_img):
        """Normalize image intensity range to [0, 255] uint8."""
        normalized = cv2.normalize(gray_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        return normalized.astype(np.uint8)

    def process_pipeline(self, image_path, output_dir=config.OUTPUT_FOLDER, filename_prefix="proc"):
        """
        Full Classical Preprocessing Pipeline:
        1. Load & Resize
        2. RGB -> Grayscale
        3. Noise Reduction
        4. Gaussian Smoothing
        5. Adaptive Histogram Equalization
        6. Intensity Normalization
        
        Returns dict containing intermediate images and saved filepaths.
        """
        bgr_orig = self.load_image(image_path)
        bgr_resized = self.resize_aspect_ratio(bgr_orig)
        
        gray = self.to_grayscale(bgr_resized)
        denoised = self.reduce_noise(gray, ksize=3)
        blurred = self.apply_gaussian_blur(denoised)
        equalized = self.apply_histogram_equalization(blurred)
        normalized = self.normalize_image(equalized)
        
        # Save processed result to disk
        proc_filename = f"{filename_prefix}_processed.png"
        proc_filepath = os.path.join(output_dir, proc_filename)
        cv2.imwrite(proc_filepath, normalized)
        
        h, w = bgr_resized.shape[:2]
        file_size = os.path.getsize(image_path)
        
        return {
            'bgr_original': bgr_resized,
            'grayscale': normalized,
            'processed_filepath': proc_filepath,
            'width': w,
            'height': h,
            'file_size': file_size
        }
