from flask import render_template
from modules.inventory import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='Inventory',
        module_desc='Real-time stock tracking across all warehouses and locations.',
        module_features=['Stock levels by location', 'Goods-in / Goods-out', 'Stock adjustments', 'Reorder point alerts', 'Lot and batch tracking'],
    )
