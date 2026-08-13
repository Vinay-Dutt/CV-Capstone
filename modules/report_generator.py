import os
import csv
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, HRFlowable
import config

class ReportGenerator:
    """
    Automated Report Generator for PDF, CSV, and Excel Export formats.
    """
    
    def __init__(self, report_dir=config.REPORT_FOLDER):
        self.report_dir = report_dir
        os.makedirs(self.report_dir, exist_ok=True)

    def export_csv(self, analysis_data, filename_prefix="report"):
        """Generates a structured CSV report."""
        csv_filepath = os.path.join(self.report_dir, f"{filename_prefix}.csv")
        
        headers = [
            "Analysis ID", "Filename", "Width", "Height", "File Size (Bytes)",
            "Upload Date", "Edge Density", "Contour Count", "Contour Area Ratio",
            "GLCM Contrast", "GLCM Correlation", "GLCM Energy", "GLCM Homogeneity",
            "Shannon Entropy", "Intensity Mean", "Intensity Variance", "Intensity Std Dev",
            "ICI Score", "Complexity Level"
        ]
        
        row_data = [
            analysis_data.get('analysis_id'),
            analysis_data.get('filename'),
            analysis_data.get('image_width'),
            analysis_data.get('image_height'),
            analysis_data.get('file_size_bytes'),
            analysis_data.get('upload_date'),
            analysis_data.get('edge_density'),
            analysis_data.get('contour_count'),
            analysis_data.get('contour_area_ratio'),
            analysis_data.get('glcm_contrast'),
            analysis_data.get('glcm_correlation'),
            analysis_data.get('glcm_energy'),
            analysis_data.get('glcm_homogeneity'),
            analysis_data.get('shannon_entropy'),
            analysis_data.get('intensity_mean'),
            analysis_data.get('intensity_variance'),
            analysis_data.get('intensity_std_dev'),
            analysis_data.get('ici_score'),
            analysis_data.get('complexity_level')
        ]
        
        with open(csv_filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerow(row_data)
            
        return csv_filepath

    def export_excel(self, analysis_data, filename_prefix="report"):
        """Generates a styled Excel (.xlsx) report using pandas."""
        excel_filepath = os.path.join(self.report_dir, f"{filename_prefix}.xlsx")
        
        df_summary = pd.DataFrame([{
            'Analysis ID': analysis_data.get('analysis_id'),
            'Image Filename': analysis_data.get('filename'),
            'Resolution': f"{analysis_data.get('image_width')} x {analysis_data.get('image_height')}",
            'ICI Score': analysis_data.get('ici_score'),
            'Complexity Level': analysis_data.get('complexity_level'),
            'Processing Time (ms)': analysis_data.get('processing_time_ms')
        }])
        
        df_features = pd.DataFrame([{
            'Edge Density': analysis_data.get('edge_density'),
            'Contour Count': analysis_data.get('contour_count'),
            'Contour Area Ratio': analysis_data.get('contour_area_ratio'),
            'GLCM Contrast': analysis_data.get('glcm_contrast'),
            'GLCM Correlation': analysis_data.get('glcm_correlation'),
            'GLCM Energy': analysis_data.get('glcm_energy'),
            'GLCM Homogeneity': analysis_data.get('glcm_homogeneity'),
            'Shannon Entropy': analysis_data.get('shannon_entropy'),
            'Intensity Mean': analysis_data.get('intensity_mean'),
            'Intensity Variance': analysis_data.get('intensity_variance'),
            'Intensity Standard Deviation': analysis_data.get('intensity_std_dev')
        }])
        
        with pd.ExcelWriter(excel_filepath, engine='openpyxl') as writer:
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            df_features.to_excel(writer, sheet_name='Feature Table', index=False)
            
        return excel_filepath

    def export_bulk_csv(self, all_analyses, filename_prefix="bulk_dataset_report"):
        """Generates a CSV report containing all historical image analysis records."""
        csv_filepath = os.path.join(self.report_dir, f"{filename_prefix}.csv")
        
        headers = [
            "Analysis ID", "Filename", "Width", "Height", "File Size (Bytes)",
            "Upload Date", "Edge Density", "Contour Count", "Contour Area Ratio",
            "GLCM Contrast", "GLCM Correlation", "GLCM Energy", "GLCM Homogeneity",
            "Shannon Entropy", "Intensity Mean", "Intensity Variance", "Intensity Std Dev",
            "ICI Score", "Complexity Level"
        ]
        
        rows = []
        for item in all_analyses:
            rows.append([
                item.get('analysis_id'),
                item.get('filename'),
                item.get('image_width'),
                item.get('image_height'),
                item.get('file_size_bytes'),
                item.get('upload_date'),
                item.get('edge_density'),
                item.get('contour_count'),
                item.get('contour_area_ratio'),
                item.get('glcm_contrast'),
                item.get('glcm_correlation'),
                item.get('glcm_energy'),
                item.get('glcm_homogeneity'),
                item.get('shannon_entropy'),
                item.get('intensity_mean'),
                item.get('intensity_variance'),
                item.get('intensity_std_dev'),
                item.get('ici_score'),
                item.get('complexity_level')
            ])
            
        with open(csv_filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows)
            
        return csv_filepath

    def export_bulk_excel(self, all_analyses, filename_prefix="bulk_dataset_report"):
        """Generates a multi-tab Excel (.xlsx) report containing all historical image analysis records."""
        excel_filepath = os.path.join(self.report_dir, f"{filename_prefix}.xlsx")
        
        rows = []
        for item in all_analyses:
            rows.append({
                'Analysis ID': item.get('analysis_id'),
                'Image Filename': item.get('filename'),
                'Resolution': f"{item.get('image_width')} x {item.get('image_height')}",
                'Upload Date': item.get('upload_date'),
                'Edge Density': item.get('edge_density'),
                'Contour Count': item.get('contour_count'),
                'GLCM Contrast': item.get('glcm_contrast'),
                'GLCM Energy': item.get('glcm_energy'),
                'Shannon Entropy': item.get('shannon_entropy'),
                'ICI Score': item.get('ici_score'),
                'Complexity Level': item.get('complexity_level')
            })
            
        df_all = pd.DataFrame(rows)
        with pd.ExcelWriter(excel_filepath, engine='openpyxl') as writer:
            df_all.to_excel(writer, sheet_name='All Image Analyses', index=False)
            
        return excel_filepath

    def export_pdf(self, analysis_data, filename_prefix="report"):
        """Generates a professional academic/industry PDF assessment report using ReportLab."""
        pdf_filepath = os.path.join(self.report_dir, f"{filename_prefix}.pdf")
        doc = SimpleDocTemplate(pdf_filepath, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#1a252f'),
            spaceAfter=6
        )
        subtitle_style = ParagraphStyle(
            'DocSubTitle',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=15
        )
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceBefore=10,
            spaceAfter=8
        )
        
        story = []
        
        # Header Title
        story.append(Paragraph("Image Complexity Index (ICI) Assessment Report", title_style))
        story.append(Paragraph(f"CapStone Engineering Project | ID: {analysis_data.get('analysis_id')} | Generated: {analysis_data.get('upload_date')}", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3498db'), spaceAfter=15))
        
        # Overview Summary Table
        summary_table_data = [
            [Paragraph("<b>Parameter</b>", styles['Normal']), Paragraph("<b>Value</b>", styles['Normal'])],
            ["Target Filename", analysis_data.get('filename')],
            ["Resolution", f"{analysis_data.get('image_width')} x {analysis_data.get('image_height')} px"],
            ["ICI Complexity Score", f"<b>{analysis_data.get('ici_score')} / 100</b>"],
            ["Assigned Level", f"<b>{analysis_data.get('complexity_level')}</b>"],
            ["Processing Latency", f"{analysis_data.get('processing_time_ms', 0):.2f} ms"]
        ]
        
        t_summary = Table(summary_table_data, colWidths=[180, 340])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (1,0), colors.HexColor('#ecf0f1')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#bdc3c7')),
            ('PADDING', (0,0), (-1,-1), 6),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ]))
        story.append(t_summary)
        story.append(Spacer(1, 15))
        
        # Extracted Features Table
        story.append(Paragraph("Extracted Computer Vision Visual Features", heading_style))
        feature_rows = [
            [Paragraph("<b>Category</b>", styles['Normal']), Paragraph("<b>Feature Metric</b>", styles['Normal']), Paragraph("<b>Extracted Value</b>", styles['Normal'])],
            ["Structural", "Canny Edge Density", f"{analysis_data.get('edge_density', 0):.5f}"],
            ["Structural", "Contour Count", str(analysis_data.get('contour_count', 0))],
            ["Structural", "Contour Area Ratio", f"{analysis_data.get('contour_area_ratio', 0):.5f}"],
            ["Textural (GLCM)", "Contrast", f"{analysis_data.get('glcm_contrast', 0):.4f}"],
            ["Textural (GLCM)", "Correlation", f"{analysis_data.get('glcm_correlation', 0):.4f}"],
            ["Textural (GLCM)", "Energy", f"{analysis_data.get('glcm_energy', 0):.4f}"],
            ["Textural (GLCM)", "Homogeneity", f"{analysis_data.get('glcm_homogeneity', 0):.4f}"],
            ["Information", "Shannon Entropy (bits/pixel)", f"{analysis_data.get('shannon_entropy', 0):.4f}"],
            ["Statistical", "Intensity Mean", f"{analysis_data.get('intensity_mean', 0):.2f}"],
            ["Statistical", "Intensity Variance", f"{analysis_data.get('intensity_variance', 0):.2f}"],
            ["Statistical", "Intensity Standard Deviation", f"{analysis_data.get('intensity_std_dev', 0):.2f}"]
        ]
        
        t_feat = Table(feature_rows, colWidths=[120, 240, 160])
        t_feat.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#bdc3c7')),
            ('PADDING', (0,0), (-1,-1), 5),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9f9f9')])
        ]))
        story.append(t_feat)
        story.append(Spacer(1, 15))
        
        # Visualizations (Dashboard chart / graph)
        graph_path = analysis_data.get('graph_filepath')
        if graph_path and os.path.exists(graph_path):
            story.append(Paragraph("Visual Analysis Decomposition & Distribution", heading_style))
            try:
                story.append(RLImage(graph_path, width=520, height=340))
            except Exception:
                pass
                
        doc.build(story)
        return pdf_filepath
