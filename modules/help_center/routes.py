from flask import render_template
from modules.help_center import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='Help Center',
        module_desc='User guides, FAQs, and support resources.',
        module_features=['User guides', 'Video tutorials', 'FAQ database', 'Support ticket system', 'Release notes'],
    )
