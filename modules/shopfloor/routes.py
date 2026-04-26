from flask import render_template
from modules.shopfloor import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='Shopfloor',
        module_desc='Digital shopfloor boards, checks, and real-time production data.',
        module_features=['Digital production boards', 'Shift handover notes', 'Hourly output tracking', 'Hygiene check logs', 'Foreign body check records'],
    )
