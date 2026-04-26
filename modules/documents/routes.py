from flask import render_template
from modules.documents import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='Documents',
        module_desc='Central document management with version control and approvals.',
        module_features=['Document register', 'Version control', 'Approval workflows', 'Distribution lists', 'Expiry alerts'],
    )
