import os
import hashlib
import logging
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError, Exception) as e:
    logger.warning(f"WeasyPrint not available. Will fallback to HTML generation. Error: {e}")
    WEASYPRINT_AVAILABLE = False

class ReportGenerator:
    def __init__(self, template_dir: str):
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))
    
    def _render_template(self, template_name: str, context: dict) -> str:
        """Render Jinja2 template to HTML string."""
        template = self.env.get_template(template_name)
        # Inject common variables
        context['generated_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        if 'report_hash' not in context:
            context['report_hash'] = 'PENDING'
        return template.render(**context)
    
    def _html_to_pdf(self, html_content: str, output_path: str) -> str:
        """Convert HTML string to PDF file using WeasyPrint or fallback to HTML."""
        if WEASYPRINT_AVAILABLE:
            HTML(string=html_content).write_pdf(output_path)
            return output_path
        else:
            # Fallback for Windows/missing GTK dependencies
            html_out = output_path.replace('.pdf', '.html')
            with open(html_out, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.warning(f"Saved as HTML instead of PDF: {html_out}")
            return html_out

    def _compute_file_hash(self, file_path: str) -> str:
        """Compute SHA-256 hash of file contents."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    async def generate_carbon_report(self, db_session, assessment_id: str) -> dict:
        """Generate PDF report for Carbon Assessment."""
        # TODO: Replace with actual DB queries and CarbonCalculator logic
        # Mocking data for now
        context = {
            "project": {
                "name": "Demo Forest MRV",
                "methodology": "VM0047",
                "organization": "Ashtalakshmi Forestry",
                "location_desc": "Assam Region",
                "total_area_ha": 5000.0
            },
            "assessment": {
                "epoch_name": "2025 Annual Monitoring",
                "start_date": "2025-01-01",
                "end_date": "2025-12-31"
            },
            "strata": [
                {"id": "S1", "forest_type": "Dense Evergreen", "area_ha": 3000, "description": "Undisturbed primary forest"},
                {"id": "S2", "forest_type": "Degraded", "area_ha": 2000, "description": "Secondary growth"}
            ],
            "plots": list(range(50)),
            "total_trees": 1250,
            "carbon_summary": {
                "net_credits": 14250.00,
                "gross_tco2e": 16000.00,
                "strata_results": [
                    {"stratum_id": "S1", "mean_agbd": 150.5, "total_agb": 451500, "total_bgb": 90300, "total_carbon": 254646},
                    {"stratum_id": "S2", "mean_agbd": 85.2, "total_agb": 170400, "total_bgb": 34080, "total_carbon": 96105}
                ],
                "uncertainty": {
                    "sampling": 8.5,
                    "measurement": 2.0,
                    "model": 5.0,
                    "total": 10.1,
                    "deduction_tco2e": 750.0
                },
                "risk_score": "LOW",
                "buffer_pct": 10.0,
                "buffer_tco2e": 1000.0
            },
            "provenance": {
                "model_version": "v1.2.0-lgbm",
                "commit_hash": "a1b2c3d4e5f6",
                "data_hash": "sha256:8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4"
            }
        }
        
        # Render HTML
        html_str = self._render_template("report_carbon_assessment.html", context)
        
        # Temp save for PDF generation
        tmp_dir = "/tmp" if os.name != 'nt' else os.environ.get('TEMP', '.')
        out_file = os.path.join(tmp_dir, f"carbon_report_{assessment_id}.pdf")
        
        # Convert to PDF
        actual_path = self._html_to_pdf(html_str, out_file)
        
        # Hash
        file_hash = self._compute_file_hash(actual_path)
        
        # Optional: Re-render with hash included in footer, re-generate PDF
        context['report_hash'] = file_hash
        html_str = self._render_template("report_carbon_assessment.html", context)
        actual_path = self._html_to_pdf(html_str, actual_path)
        final_hash = self._compute_file_hash(actual_path)
        
        # TODO: Upload to MinIO here
        # s3_client.upload_file(actual_path, bucket, f"reports/{assessment_id}.pdf")
        
        return {
            "pdf_path": actual_path,
            "pdf_url": f"s3://mrv-reports/{assessment_id}.pdf",
            "report_hash": final_hash,
            "generated_at": context['generated_at']
        }

    async def generate_field_report(self, db_session, project_id: str) -> dict:
        """Generate PDF report for Field Verification Summary."""
        # Mocking data
        context = {
            "project": {"name": "Demo Forest MRV"},
            "survey": {
                "start_date": "2025-10-01",
                "end_date": "2025-10-15",
                "surveyors": ["Alice", "Bob", "Charlie"]
            },
            "plots": [
                {"code": "P01", "lat": 26.1, "lon": 91.7, "elevation": 150, "stratum": "S1", "tree_count": 25},
                {"code": "P02", "lat": 26.15, "lon": 91.75, "elevation": 160, "stratum": "S2", "tree_count": 18},
            ],
            "species_stats": [
                {"scientific_name": "Shorea robusta", "count": 150, "mean_dbh": 45.2, "mean_height": 22.5},
                {"scientific_name": "Tectona grandis", "count": 85, "mean_dbh": 35.1, "mean_height": 18.0}
            ],
            "plot_biomass": [
                {"plot_code": "P01", "basal_area_ha": 25.5, "agb_kg": 15000.0, "agbd_tha": 300.0},
                {"plot_code": "P02", "basal_area_ha": 18.2, "agb_kg": 8500.0, "agbd_tha": 170.0}
            ],
            "qa": {
                "mean_gps_acc": 3.2,
                "max_gps_acc": 8.5,
                "completeness_pct": 98.5,
                "outliers_flagged": 2
            },
            "sample_trees": [
                {"plot_code": "P01", "tag_number": "T001", "species": "Shorea robusta", "dbh": 55.4, "health": "HEALTHY"}
            ]
        }
        
        html_str = self._render_template("report_field_summary.html", context)
        
        tmp_dir = "/tmp" if os.name != 'nt' else os.environ.get('TEMP', '.')
        out_file = os.path.join(tmp_dir, f"field_report_{project_id}.pdf")
        
        actual_path = self._html_to_pdf(html_str, out_file)
        
        file_hash = self._compute_file_hash(actual_path)
        context['report_hash'] = file_hash
        html_str = self._render_template("report_field_summary.html", context)
        actual_path = self._html_to_pdf(html_str, actual_path)
        final_hash = self._compute_file_hash(actual_path)
        
        return {
            "pdf_path": actual_path,
            "pdf_url": f"s3://mrv-reports/field_{project_id}.pdf",
            "report_hash": final_hash,
            "generated_at": context['generated_at']
        }
