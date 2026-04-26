from flask import render_template
from modules.pricing import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='Pricing',
        module_desc='Manage product costings, margin calculations, and price lists.',
        module_features=['Bill of Materials costing', 'Margin analysis by product', 'Price list management', 'Multi-currency support', 'Supplier price tracking'],
    )
