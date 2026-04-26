from flask import render_template
from modules.supply_chain import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='Supply Chain',
        module_desc='Manage purchase orders, lead times, and supply risk.',
        module_features=['Purchase order management', 'Lead time tracking', 'Supply risk assessment', 'Preferred supplier management', 'Delivery performance'],
    )
