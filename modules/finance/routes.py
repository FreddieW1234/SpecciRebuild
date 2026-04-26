from flask import render_template
from modules.finance import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='Finance',
        module_desc='Track invoices, costs, and financial performance.',
        module_features=['Invoice management', 'Cost tracking', 'Budget vs actuals', 'Currency management', 'Financial reporting'],
    )
