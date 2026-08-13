import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from modules.preprocessing import ImagePreprocessor
from modules.feature_extraction import FeatureExtractor
from modules.complexity_score import ComplexityScorer
import config

class ImageComparer:
    """
    Multi-Image Complexity Assessment, Ranking, and Extrema Detection Engine.
    """
    
    def __init__(self):
        self.preprocessor = ImagePreprocessor()
        self.extractor = FeatureExtractor()
        self.scorer = ComplexityScorer()

    def compare_images(self, image_paths, output_dir=config.OUTPUT_FOLDER):
        """
        Process a list of image filepaths, rank them by ICI score, and identify extrema.
        Returns detailed comparison dict including chart filepaths.
        """
        results = []
        
        for idx, path in enumerate(image_paths):
            filename = os.path.basename(path)
            prefix = f"comp_{idx}"
            
            # Run processing pipeline
            prep_data = self.preprocessor.process_pipeline(path, output_dir=output_dir, filename_prefix=prefix)
            gray = prep_data['grayscale']
            
            features = self.extractor.extract_all_features(gray, output_dir=output_dir, filename_prefix=prefix)
            score_data = self.scorer.compute_ici(features)
            
            results.append({
                'filename': filename,
                'filepath': path,
                'processed_filepath': prep_data['processed_filepath'],
                'edge_filepath': features['edge_filepath'],
                'width': prep_data['width'],
                'height': prep_data['height'],
                'file_size': prep_data['file_size'],
                'features': features,
                'ici_score': score_data['ici_score'],
                'complexity_level': score_data['complexity_level'],
                'badge_class': score_data['badge_class'],
                'color_hex': score_data['color_hex'],
                'sub_scores': score_data['sub_scores']
            })
            
        # Sort by ICI score descending (Rank 1 = Highest Complexity)
        ranked = sorted(results, key=lambda x: x['ici_score'], reverse=True)
        
        for rank_idx, item in enumerate(ranked, start=1):
            item['rank'] = rank_idx
            
        highest = ranked[0] if ranked else None
        lowest = ranked[-1] if ranked else None
        
        # Generate comparative graph figure
        comp_graph_filepath = self.generate_comparison_chart(ranked)
        
        return {
            'count': len(ranked),
            'ranked_images': ranked,
            'highest_complexity': highest,
            'lowest_complexity': lowest,
            'comparison_graph_filepath': comp_graph_filepath
        }

    def generate_comparison_chart(self, ranked_items, filename_prefix="multi_comp"):
        """Generates a comparison bar chart ranking images by ICI score."""
        if not ranked_items:
            return None
            
        fig, ax = plt.subplots(figsize=(10, 5), dpi=120)
        
        names = [item['filename'][:15] + ('...' if len(item['filename']) > 15 else '') for item in ranked_items]
        scores = [item['ici_score'] for item in ranked_items]
        colors = [item['color_hex'] for item in ranked_items]
        
        bars = ax.barh(names[::-1], scores[::-1], color=colors[::-1], height=0.55)
        ax.set_xlim(0, 100)
        ax.set_xlabel('Image Complexity Index (ICI)', fontsize=11, fontweight='bold')
        ax.set_title('Comparative Image Complexity Ranking', fontsize=13, fontweight='bold')
        
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 1.5, bar.get_y() + bar.get_height()/2.0, f'{width:.1f}', ha='left', va='center', fontsize=10, fontweight='bold')
            
        plt.tight_layout()
        
        graph_filepath = os.path.join(config.GRAPH_FOLDER, f"{filename_prefix}_chart.png")
        plt.savefig(graph_filepath, bbox_inches='tight', facecolor='#ffffff', edgecolor='none')
        plt.close(fig)
        
        return graph_filepath
