from flask import render_template
from modules.sales import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='Sales',
        module_desc='Manage customer orders, quotes, and delivery performance.',
        module_features=['Customer order management', 'Quoting and pricing', 'Delivery scheduling', 'Sales performance reporting', 'Customer product lists'],
    )
