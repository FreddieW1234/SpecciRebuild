from flask import render_template, redirect, url_for
from modules.dashboard import bp
from core.db import query_one
from core.decorators import login_required


@bp.route('/')
@login_required
def index():
    stats = {
        'components': query_one('SELECT COUNT(*) as cnt FROM components')['cnt'],
        'suppliers': query_one('SELECT COUNT(*) as cnt FROM suppliers')['cnt'],
        'active_components': query_one("SELECT COUNT(*) as cnt FROM components WHERE status = 'Active'")['cnt'],
        'approved_suppliers': query_one("SELECT COUNT(*) as cnt FROM suppliers WHERE approval_status = 'approved'")['cnt'],
    }
    recent_components = []
    from core.db import query_all
    recent_components = query_all(
        'SELECT id, code, name, component_type, status, updated_at FROM components ORDER BY updated_at DESC LIMIT 5'
    )
    return render_template('dashboard/index.html', stats=stats, recent_components=recent_components)


@bp.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('dashboard.index'))
