from flask import render_template, request, redirect, url_for, flash, g, abort
from modules.users import bp
from core.decorators import login_required
from core.auth import hash_password
from core.db import query_one, query_all, execute, execute_returning

ROLES = ['admin', 'user', 'viewer']


def _require_admin():
    if not g.get('current_user') or g.current_user.get('role') != 'admin':
        abort(403)


@bp.route('/')
@login_required
def index():
    _require_admin()
    users = query_all('SELECT * FROM users ORDER BY username')
    return render_template('users/index.html', users=users)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    _require_admin()
    if request.method == 'POST':
        data = request.form.to_dict()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not username or not email or not password:
            flash('Username, email, and password are required.', 'error')
            return render_template('users/form.html', user=data, is_new=True, roles=ROLES)
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('users/form.html', user=data, is_new=True, roles=ROLES)

        existing = query_one('SELECT id FROM users WHERE username=%s OR email=%s', (username, email))
        if existing:
            flash('A user with that username or email already exists.', 'error')
            return render_template('users/form.html', user=data, is_new=True, roles=ROLES)

        pw_hash = hash_password(password)
        execute_returning('''
            INSERT INTO users
                (username, email, password_hash, role, display_name, position, work_phone, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        ''', (
            username, email, pw_hash,
            data.get('role', 'user'),
            data.get('display_name') or None,
            data.get('position') or None,
            data.get('work_phone') or None,
            data.get('is_active') == 'on',
        ))
        flash(f'User "{username}" created.', 'success')
        return redirect(url_for('users.index'))
    return render_template('users/form.html', user={}, is_new=True, roles=ROLES)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    _require_admin()
    user = query_one('SELECT * FROM users WHERE id = %s', (id,))
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('users.index'))

    if request.method == 'POST':
        data = request.form.to_dict()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()

        if not username or not email:
            flash('Username and email are required.', 'error')
            return render_template('users/form.html', user=data, is_new=False, roles=ROLES)

        # Check for duplicate username/email on a different account
        conflict = query_one(
            'SELECT id FROM users WHERE (username=%s OR email=%s) AND id != %s',
            (username, email, id)
        )
        if conflict:
            flash('Another user with that username or email already exists.', 'error')
            return render_template('users/form.html', user=data, is_new=False, roles=ROLES)

        # Build update — password only changes if provided
        password = data.get('password', '').strip()
        if password:
            if len(password) < 8:
                flash('Password must be at least 8 characters.', 'error')
                return render_template('users/form.html', user=data, is_new=False, roles=ROLES)
            pw_hash = hash_password(password)
            execute('''
                UPDATE users SET
                    username=%s, email=%s, password_hash=%s, role=%s,
                    display_name=%s, position=%s, work_phone=%s, is_active=%s
                WHERE id=%s
            ''', (
                username, email, pw_hash,
                data.get('role', 'user'),
                data.get('display_name') or None,
                data.get('position') or None,
                data.get('work_phone') or None,
                data.get('is_active') == 'on',
                id,
            ))
        else:
            execute('''
                UPDATE users SET
                    username=%s, email=%s, role=%s,
                    display_name=%s, position=%s, work_phone=%s, is_active=%s
                WHERE id=%s
            ''', (
                username, email,
                data.get('role', 'user'),
                data.get('display_name') or None,
                data.get('position') or None,
                data.get('work_phone') or None,
                data.get('is_active') == 'on',
                id,
            ))
        flash(f'User "{username}" updated.', 'success')
        return redirect(url_for('users.index'))

    return render_template('users/form.html', user=user, is_new=False, roles=ROLES)


@bp.route('/<int:id>/toggle-active', methods=['POST'])
@login_required
def toggle_active(id):
    _require_admin()
    user = query_one('SELECT * FROM users WHERE id = %s', (id,))
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('users.index'))
    if user['id'] == g.current_user['id']:
        flash("You can't deactivate your own account.", 'error')
        return redirect(url_for('users.index'))
    new_state = not user['is_active']
    execute('UPDATE users SET is_active=%s WHERE id=%s', (new_state, id))
    flash(f'User "{user["username"]}" {"activated" if new_state else "deactivated"}.', 'success')
    return redirect(url_for('users.index'))
