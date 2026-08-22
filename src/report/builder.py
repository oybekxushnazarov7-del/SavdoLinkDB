"""
Vazifasi: HTML hisobotlarni generatori.
"""
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from .filters import register_filters
from .data_source import (
    get_kpi_summary, get_top_products, get_store_ranking,
    get_store_detail, get_dq_metrics, get_load_history
)

class ReportBuilder:
    def __init__(self, config: dict, cursor):
        self.cfg = config
        self.cur = cursor
        
        templates_dir = Path(self.cfg.get("paths", {}).get("templates", "templates"))
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        register_filters(self.env)

    def _render(self, template_name: str, context: dict, out_name: str) -> Path:
        context.setdefault("generated_at", datetime.now())
        template = self.env.get_template(template_name)
        html_content = template.render(**context)
        
        out_dir = Path(self.cfg.get("paths", {}).get("reports", "reports"))
        out_dir.mkdir(parents=True, exist_ok=True)
        
        out_path = out_dir / out_name
        out_path.write_text(html_content, encoding="utf-8")
        return out_path

    def build_dashboard(self, date_from: str, date_to: str) -> Path:
        kpi = get_kpi_summary(self.cur, date_from, date_to)
        top_products = get_top_products(self.cur, date_from, date_to, limit=10)
        stores = get_store_ranking(self.cur, date_from, date_to)
        context = {
            "period_label": f"{date_from} — {date_to}",
            "kpi": kpi,
            "top_products": top_products,
            "stores": stores,
        }
        return self._render("dashboard.html", context, "dashboard.html")

    def build_store_report(self, store_code: str, date_from: str, date_to: str) -> Path:
        store_info = get_store_detail(self.cur, store_code, date_from, date_to)
        context = {
            "period_label": f"{date_from} — {date_to}",
            "store": store_info
        }
        return self._render("store_report.html", context, f"store_{store_code}.html")

    def build_dq_report(self, load_id: str) -> Path:
        dq_data = get_dq_metrics(self.cur, load_id)
        context = {"load_id": load_id, "dq": dq_data}
        return self._render("dq_report.html", context, "dq_report.html")

    def build_load_log(self, limit: int = 30) -> Path:
        logs = get_load_history(self.cur, limit)
        context = {"logs": logs}
        return self._render("load_log.html", context, "load_log.html")