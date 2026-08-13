import os
import matplotlib
matplotlib.use('Agg')  # Headless backend for web servers
import matplotlib.pyplot as plt
import numpy as np
import cv2
import config

class Visualizer:
    """
    Visualization engine that creates Matplotlib figures for web dashboard embedding and report generation.
    """
    
    def __init__(self, graph_dir=config.GRAPH_FOLDER):
        self.graph_dir = graph_dir
        os.makedirs(self.graph_dir, exist_ok=True)
        # Apply clean dark-aware style
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

    def generate_analysis_dashboard_graph(self, features, ici_result, filename_prefix="graph"):
        """
        Generates a 4-panel summary graph figure:
        1. Sub-score breakdown bar chart
        2. Feature values radar chart
        3. Color / Intensity Distribution
        4. Complexity Scale Gauge Indicator
        """
        fig = plt.figure(figsize=(12, 8), dpi=120)
        fig.patch.set_facecolor('#ffffff')
        
        # Panel 1: Sub-scores
        ax1 = plt.subplot(2, 2, 1)
        sub_scores = ici_result['sub_scores']
        categories = ['Spatial\nEdge/Contour', 'Texture\nGLCM', 'Information\nEntropy']
        values = [
            sub_scores['spatial_structural'],
            sub_scores['texture_glcm'],
            sub_scores['information_entropy']
        ]
        colors = ['#4e73df', '#1cc88a', '#36b9cc']
        bars = ax1.bar(categories, values, color=colors, width=0.5)
        ax1.set_ylim(0, 100)
        ax1.set_ylabel('Sub-Score (0-100)', fontsize=10, fontweight='bold')
        ax1.set_title('Complexity Sub-domain Decomposition', fontsize=12, fontweight='bold')
        for bar in bars:
            yval = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 2, f'{yval:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
            
        # Panel 2: Normalized Radar Chart
        ax2 = plt.subplot(2, 2, 2, polar=True)
        radar_labels = ['Edge Density', 'Contour Area', 'GLCM Contrast', 'GLCM Entropy', 'Shannon Ent.', 'Variance']
        radar_vals = [
            sub_scores['s_edge'],
            sub_scores['s_contour'],
            sub_scores['s_contrast'],
            sub_scores['s_entropy'],
            sub_scores['s_entropy'],
            sub_scores['s_var']
        ]
        num_vars = len(radar_labels)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        radar_vals += radar_vals[:1]
        angles += angles[:1]
        
        ax2.plot(angles, radar_vals, color='#e74a3b', linewidth=2, linestyle='solid')
        ax2.fill(angles, radar_vals, color='#e74a3b', alpha=0.25)
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(radar_labels, fontsize=8)
        ax2.set_yticks([20, 40, 60, 80, 100])
        ax2.set_title('Feature Distribution Radar', fontsize=12, fontweight='bold', pad=15)
        
        # Panel 3: Intensity Histogram
        ax3 = plt.subplot(2, 2, 3)
        gray_img = features.get('gray_img')
        if gray_img is not None:
            counts, bins = np.histogram(gray_img.flatten(), bins=64, range=(0, 256))
            ax3.fill_between(bins[:-1], counts, color='#4e73df', alpha=0.6)
            ax3.plot(bins[:-1], counts, color='#2e59d9', linewidth=1.5)
            ax3.set_xlim(0, 255)
            ax3.set_xlabel('Pixel Intensity (0-255)', fontsize=10)
            ax3.set_ylabel('Pixel Frequency', fontsize=10)
            ax3.set_title('Pixel Intensity Histogram', fontsize=12, fontweight='bold')
        else:
            ax3.text(0.5, 0.5, 'Histogram Data Unavailable', ha='center', va='center')

        # Panel 4: Overall ICI Scale Indicator
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        score = ici_result['ici_score']
        level = ici_result['complexity_level']
        color = ici_result['color_hex']
        
        # Draw background meter bar
        ax4.add_patch(plt.Rectangle((0.1, 0.4), 0.8, 0.2, color='#eaecf4', ec='none'))
        fill_width = 0.8 * (score / 100.0)
        ax4.add_patch(plt.Rectangle((0.1, 0.4), fill_width, 0.2, color=color, ec='none'))
        
        ax4.text(0.5, 0.75, f"ICI Score: {score:.1f} / 100", ha='center', va='center', fontsize=16, fontweight='bold', color='#2e384d')
        ax4.text(0.5, 0.2, f"Classification: {level}", ha='center', va='center', fontsize=14, fontweight='bold', color=color)
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.set_title('Final Image Complexity Index (ICI)', fontsize=12, fontweight='bold')

        plt.tight_layout()
        
        graph_filename = f"{filename_prefix}_dashboard.png"
        graph_filepath = os.path.join(self.graph_dir, graph_filename)
        plt.savefig(graph_filepath, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)
        
        return graph_filepath
