from flask import render_template
from modules.rnd import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='R&D',
        module_desc='Manage product development projects, trials, and formulation changes.',
        module_features=['Product development projects', 'Trial management', 'Formulation versioning', 'Scale-up records', 'NPD stage gate process'],
    )
