import math
import config

class ComplexityScorer:
    """
    Mathematical Image Complexity Index (ICI) Generation & Classification Engine.
    Fuses normalized structural, textural, and statistical features using a weighted model.
    Scales complexity score smoothly from 0.0 to 100.0.
    """
    
    def __init__(self, weights=config.ICI_FEATURE_WEIGHTS):
        self.weights = weights

    def normalize_feature(self, value, min_val, max_val, curve="linear"):
        """
        Clips and maps feature value into normalized [0.0, 100.0] domain.
        Supports logarithmic and sigmoid response curves for natural perception.
        """
        clipped = max(min_val, min(value, max_val))
        normalized = (clipped - min_val) / float(max_val - min_val) if max_val > min_val else 0.0
        
        if curve == "log":
            # Non-linear logarithmic scaling for high variance metrics like GLCM Contrast
            normalized = math.log1p(normalized * 9.0) / math.log1p(9.0)
        elif curve == "sigmoid":
            # Sigmoidal response around midpoint
            x = (normalized - 0.5) * 6.0
            normalized = 1.0 / (1.0 + math.exp(-x))
            
        return normalized * 100.0

    def compute_ici(self, features):
        """
        Calculates the final Image Complexity Index (ICI) on a 0-100 scale.
        
        Formula:
        ICI = w_edge * S_edge + w_contour * S_contour + w_contrast * S_contrast
            + w_glcm_ent * S_glcm_ent + w_entropy * S_entropy + w_var * S_var
        """
        # Normalized Component Scores (0 to 100)
        # Edge density typically ranges from 0.005 (smooth) to 0.25 (highly detailed)
        s_edge = self.normalize_feature(features.get('edge_density', 0), 0.005, 0.22, curve="linear")
        
        # Contour count & area ratio metric
        cnt_count = features.get('contour_count', 0)
        s_contour = self.normalize_feature(cnt_count, 10, 1500, curve="log")
        
        # GLCM Contrast (0.1 to 35.0+)
        contrast = features.get('glcm_contrast', 0)
        s_contrast = self.normalize_feature(contrast, 0.1, 25.0, curve="log")
        
        # GLCM Entropy derived from 1 - Homogeneity / Energy
        glcm_entropy = (1.0 - features.get('glcm_homogeneity', 0.5)) * 100.0
        s_glcm_ent = min(100.0, max(0.0, glcm_entropy))
        
        # Shannon Entropy typically ranges from 1.0 (flat) to 8.0 (maximum randomness)
        entropy = features.get('shannon_entropy', 0)
        s_entropy = self.normalize_feature(entropy, 2.0, 7.8, curve="linear")
        
        # Intensity Variance (10.0 to 6000.0)
        variance = features.get('intensity_variance', 0)
        s_var = self.normalize_feature(variance, 50.0, 4500.0, curve="log")
        
        # Weighted Fusion
        ici_score = (
            self.weights['edge_density'] * s_edge +
            self.weights['contour_density'] * s_contour +
            self.weights['glcm_contrast'] * s_contrast +
            self.weights['glcm_entropy'] * s_glcm_ent +
            self.weights['shannon_entropy'] * s_entropy +
            self.weights['intensity_variance'] * s_var
        )
        
        ici_score = round(max(0.0, min(100.0, ici_score)), 2)
        level_info = self.classify_complexity(ici_score)
        
        # Sub-score category aggregation for dashboard breakdown
        spatial_complexity = round((s_edge * 0.55 + s_contour * 0.45), 2)
        texture_complexity = round((s_contrast * 0.5 + s_glcm_ent * 0.5), 2)
        information_complexity = round((s_entropy * 0.7 + s_var * 0.3), 2)
        
        return {
            'ici_score': ici_score,
            'complexity_level': level_info['name'],
            'badge_class': level_info['badge'],
            'color_hex': level_info['color'],
            'sub_scores': {
                'spatial_structural': spatial_complexity,
                'texture_glcm': texture_complexity,
                'information_entropy': information_complexity,
                's_edge': round(s_edge, 2),
                's_contour': round(s_contour, 2),
                's_contrast': round(s_contrast, 2),
                's_entropy': round(s_entropy, 2),
                's_var': round(s_var, 2)
            }
        }

    def classify_complexity(self, ici_score):
        """Classifies numerical score into standard complexity levels."""
        for level in config.COMPLEXITY_LEVELS[:-1]:
            if level['min'] <= ici_score < level['max']:
                return level
        return config.COMPLEXITY_LEVELS[-1]
