from flask import render_template
from modules.hr import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='HR',
        module_desc='Manage employees, training records, and hygiene certifications.',
        module_features=['Employee records', 'Training matrix', 'Food hygiene certificates', 'Absence management', 'Contractor management'],
    )
