from flask import render_template
from modules.marketing import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='Marketing',
        module_desc='Manage product marketing materials, claims, and campaigns.',
        module_features=['Marketing assets library', 'Claim substantiation', 'Campaign management', 'Label copy management', 'Photography library'],
    )
