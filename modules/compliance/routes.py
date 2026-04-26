from flask import render_template
from modules.compliance import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='Compliance',
        module_desc='Manage food safety standards, audits, and regulatory compliance.',
        module_features=['BRC/BRCGS compliance tracker', 'Audit management', 'Legislative monitoring', 'HACCP management', 'Regulatory submissions'],
    )
