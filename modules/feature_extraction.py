import os
import cv2
import numpy as np
from skimage.feature import graycomatrix, graycoprops
from skimage.measure import shannon_entropy
from scipy.stats import skew
import config

class FeatureExtractor:
    """
    Classical Computer Vision Visual Feature Extraction Engine.
    Extracts structural (edges, contours), textural (GLCM, entropy), and statistical features.
    """
    
    def __init__(self, low_threshold=config.DEFAULT_CANNY_LOW, high_threshold=config.DEFAULT_CANNY_HIGH):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

    def extract_canny_edges(self, gray_img):
        """
        Computes Canny Edge map and Edge Density ratio.
        Edge Density = (Count of edge pixels) / (Total pixels in image).
        """
        edge_map = cv2.Canny(gray_img, self.low_threshold, self.high_threshold)
        total_pixels = gray_img.shape[0] * gray_img.shape[1]
        edge_pixels = np.count_nonzero(edge_map)
        edge_density = float(edge_pixels) / float(total_pixels)
        return edge_map, edge_density

    def extract_contours(self, gray_img, edge_map):
        """
        Extracts structural contours, contour count, and contour area ratio.
        """
        # Find external contours from edge map
        contours, _ = cv2.findContours(edge_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour_count = len(contours)
        
        total_image_area = float(gray_img.shape[0] * gray_img.shape[1])
        total_contour_area = sum(cv2.contourArea(c) for c in contours)
        contour_area_ratio = float(total_contour_area) / total_image_area if total_image_area > 0 else 0.0
        
        # Generate visual contour overlay
        contour_canvas = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(contour_canvas, contours, -1, (0, 255, 0), 1)
        
        return contour_canvas, contour_count, contour_area_ratio

    def extract_glcm_features(self, gray_img):
        """
        Computes Gray-Level Co-occurrence Matrix (GLCM) at 0, 45, 90, 135 degrees.
        Extracts Contrast, Correlation, Energy, Homogeneity metrics.
        """
        # Quantize image to 64 levels for speed and memory efficiency
        gray_quantized = (gray_img // 4).astype(np.uint8)
        
        # Distances = [1, 3], Angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]
        glcm = graycomatrix(
            gray_quantized,
            distances=[1, 3],
            angles=[0, np.pi/4, np.pi/2, 3*np.pi/4],
            levels=64,
            symmetric=True,
            normed=True
        )
        
        contrast = float(np.mean(graycoprops(glcm, 'contrast')))
        correlation = float(np.mean(graycoprops(glcm, 'correlation')))
        energy = float(np.mean(graycoprops(glcm, 'energy')))
        homogeneity = float(np.mean(graycoprops(glcm, 'homogeneity')))
        
        # Sanitize potential NaN values from uniform regions
        contrast = 0.0 if np.isnan(contrast) else contrast
        correlation = 0.0 if np.isnan(correlation) else correlation
        energy = 0.0 if np.isnan(energy) else energy
        homogeneity = 1.0 if np.isnan(homogeneity) else homogeneity
        
        return {
            'glcm_contrast': round(contrast, 4),
            'glcm_correlation': round(correlation, 4),
            'glcm_energy': round(energy, 4),
            'glcm_homogeneity': round(homogeneity, 4)
        }

    def calculate_entropy(self, gray_img):
        """Calculates Shannon Entropy (information richness of image intensity distribution)."""
        entropy_val = float(shannon_entropy(gray_img, base=2))
        return 0.0 if np.isnan(entropy_val) else round(entropy_val, 4)

    def extract_statistical_features(self, gray_img):
        """Extracts first and second order pixel intensity statistical moments."""
        mean_val = float(np.mean(gray_img))
        variance_val = float(np.var(gray_img))
        std_dev_val = float(np.std(gray_img))
        skew_val = float(skew(gray_img.ravel()))
        
        mean_val = 0.0 if np.isnan(mean_val) else mean_val
        variance_val = 0.0 if np.isnan(variance_val) else variance_val
        std_dev_val = 0.0 if np.isnan(std_dev_val) else std_dev_val
        skew_val = 0.0 if np.isnan(skew_val) else skew_val
        
        return {
            'intensity_mean': round(mean_val, 4),
            'intensity_variance': round(variance_val, 4),
            'intensity_std_dev': round(std_dev_val, 4),
            'intensity_skewness': round(skew_val, 4)
        }

    def extract_all_features(self, gray_img, output_dir=config.OUTPUT_FOLDER, filename_prefix="feat"):
        """
        Executes complete visual feature extraction and saves edge map & contour map images.
        """
        edge_map, edge_density = self.extract_canny_edges(gray_img)
        contour_map, contour_count, contour_area_ratio = self.extract_contours(gray_img, edge_map)
        glcm_feats = self.extract_glcm_features(gray_img)
        entropy_val = self.calculate_entropy(gray_img)
        stats_feats = self.extract_statistical_features(gray_img)
        
        # Save edge image
        edge_filename = f"{filename_prefix}_edges.png"
        edge_filepath = os.path.join(output_dir, edge_filename)
        cv2.imwrite(edge_filepath, edge_map)
        
        # Save contour image
        contour_filename = f"{filename_prefix}_contours.png"
        contour_filepath = os.path.join(output_dir, contour_filename)
        cv2.imwrite(contour_filepath, contour_map)
        
        feature_dict = {
            'edge_density': round(edge_density, 5),
            'contour_count': int(contour_count),
            'contour_area_ratio': round(contour_area_ratio, 5),
            'shannon_entropy': entropy_val,
            'edge_filepath': edge_filepath,
            'contour_filepath': contour_filepath,
            **glcm_feats,
            **stats_feats
        }
        
        return feature_dict
