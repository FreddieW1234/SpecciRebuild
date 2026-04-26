from flask import render_template
from modules.traceability import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='Traceability',
        module_desc='End-to-end lot traceability from raw material to finished product.',
        module_features=['Lot traceability trees', 'Mock recall exercises', 'Supplier traceability confirmation', 'Batch genealogy reports', 'Recall and withdrawal management'],
    )
