from flask import render_template
from modules.crm import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='CRM',
        module_desc='Manage customer relationships, contacts, and communications.',
        module_features=['Customer database', 'Contact management', 'Interaction logging', 'Customer segmentation', 'Activity tracking'],
    )
