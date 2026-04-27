from flask import render_template, request, redirect, url_for, flash
from modules.equipment import bp
from core.decorators import login_required
from core.db import query_one, query_all, execute, execute_returning


def _get_all(search=None, active_filter=None):
    sql = 'SELECT * FROM equipment WHERE 1=1'
    params = []
    if search:
        sql += ' AND (tool_number ILIKE %s OR description ILIKE %s)'
        params += [f'%{search}%', f'%{search}%']
    if active_filter == 'active':
        sql += ' AND is_active = TRUE'
    elif active_filter == 'inactive':
        sql += ' AND is_active = FALSE'
    sql += ' ORDER BY tool_number'
    return query_all(sql, params or None)


def _get(eq_id):
    return query_one('SELECT * FROM equipment WHERE id = %s', (eq_id,))


@bp.route('/')
@login_required
def index():
    search = request.args.get('q', '').strip()
    active_filter = request.args.get('active', '').strip()
    items = _get_all(search=search or None, active_filter=active_filter or None)
    return render_template('equipment/index.html', items=items, search=search,
                           active_filter=active_filter)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        data = request.form.to_dict()
        if not data.get('tool_number'):
            flash('Tool number is required.', 'error')
            return render_template('equipment/form.html', eq={}, is_new=True)
        eq_id = execute_returning('''
            INSERT INTO equipment
                (tool_number, description, size_raw, supplier, unique_for, unique_until, is_active, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            data.get('tool_number'),
            data.get('description') or None,
            data.get('size_raw') or None,
            data.get('supplier') or None,
            data.get('unique_for') or None,
            data.get('unique_until') or None,
            data.get('is_active') == 'on',
            data.get('notes') or None,
        ))
        flash('Tool head created.', 'success')
        return redirect(url_for('equipment.index'))
    return render_template('equipment/form.html', eq={}, is_new=True)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    eq = _get(id)
    if not eq:
        flash('Tool head not found.', 'error')
        return redirect(url_for('equipment.index'))
    if request.method == 'POST':
        data = request.form.to_dict()
        execute('''
            UPDATE equipment SET
                tool_number=%s, description=%s, size_raw=%s, supplier=%s,
                unique_for=%s, unique_until=%s, is_active=%s, notes=%s
            WHERE id=%s
        ''', (
            data.get('tool_number'),
            data.get('description') or None,
            data.get('size_raw') or None,
            data.get('supplier') or None,
            data.get('unique_for') or None,
            data.get('unique_until') or None,
            data.get('is_active') == 'on',
            data.get('notes') or None,
            id,
        ))
        flash('Tool head updated.', 'success')
        return redirect(url_for('equipment.index'))
    return render_template('equipment/form.html', eq=eq, is_new=False)


@bp.route('/<int:id>/toggle-active', methods=['POST'])
@login_required
def toggle_active(id):
    eq = _get(id)
    if not eq:
        flash('Tool head not found.', 'error')
        return redirect(url_for('equipment.index'))
    new_state = not eq['is_active']
    execute('UPDATE equipment SET is_active=%s WHERE id=%s', (new_state, id))
    flash(f'Tool head marked {"active" if new_state else "inactive"}.', 'success')
    return redirect(url_for('equipment.index'))
