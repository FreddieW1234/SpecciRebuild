from flask import render_template
from modules.quality import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='Quality',
        module_desc='Track quality events, NCRs, CAPAs, and audit schedules.',
        module_features=['Non-conformance reports', 'Corrective actions (CAPA)', 'Audit scheduling', 'Quality KPI dashboard', 'Certificate of Analysis management'],
    )
