from flask import render_template
from modules.maintenance import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='Maintenance',
        module_desc='Schedule and track equipment maintenance and calibration.',
        module_features=['Preventive maintenance schedules', 'Equipment register', 'Calibration records', 'Breakdown logging', 'Maintenance KPIs'],
    )
