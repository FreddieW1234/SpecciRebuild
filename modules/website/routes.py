from flask import render_template
from modules.website import bp
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    return render_template('stubs/coming_soon.html',
        module_title='Website',
        module_desc='Manage your company website content, products, and pages.',
        module_features=['Product page management', 'News and blog', 'Contact information management', 'SEO metadata', 'Image management'],
    )
