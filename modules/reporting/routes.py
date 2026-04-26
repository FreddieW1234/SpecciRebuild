from flask import render_template
from modules.reporting import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='Reporting',
        module_desc='Custom reports and dashboards across all modules.',
        module_features=['Cross-module reporting', 'Custom dashboard builder', 'Scheduled reports', 'Data export (CSV/Excel)', 'KPI tracking'],
    )
