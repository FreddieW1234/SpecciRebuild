from flask import render_template
from modules.packaging import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='Packaging',
        module_desc='Manage packaging specifications, materials, and artwork approvals.',
        module_features=['Packaging material specs', 'Artwork approval workflow', 'Label compliance checks', 'Supplier packaging orders', 'Recyclability tracking'],
    )
