from flask import render_template
from modules.production import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='Production',
        module_desc='Plan and track manufacturing runs, batch records, and yields.',
        module_features=['Production planning board', 'Batch records', 'Yield and loss tracking', 'Work order management', 'Equipment scheduling'],
    )
