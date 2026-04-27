import bcrypt
from flask import Blueprint, session, redirect, url_for, request, flash, render_template, g
from core.db import query_one, query_all, execute, execute_returning

bp = Blueprint('auth', __name__)


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def login_user(user_id):
    session['user_id'] = user_id


def logout_user():
    session.clear()


def get_current_user():
    uid = session.get('user_id')
    if uid:
        return get_user_by_id(uid)
    return None


def get_user_by_id(user_id):
    return query_one('SELECT * FROM users WHERE id = %s AND is_active = TRUE', (user_id,))


def get_active_company():
    """Return the active company profile dict from the session, defaulting to id=1."""
    company_id = session.get('active_company_id', 1)
    company = query_one('SELECT * FROM company_profile WHERE id = %s', (company_id,))
    if not company:
        company = query_one('SELECT * FROM company_profile ORDER BY id LIMIT 1')
    return company


def get_all_companies():
    """Return all companies for the switcher dropdown."""
    return query_all('SELECT id, name FROM company_profile ORDER BY id')


def app_has_registered_users():
    row = query_one('SELECT COUNT(*) as cnt FROM users')
    return row and row['cnt'] > 0


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if g.get('current_user'):
        return redirect(url_for('dashboard.index'))

    if not app_has_registered_users():
        return redirect(url_for('auth.setup'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = query_one('SELECT * FROM users WHERE username = %s AND is_active = TRUE', (username,))
        if user and check_password(password, user['password_hash']):
            execute('UPDATE users SET last_login = NOW() WHERE id = %s', (user['id'],))
            login_user(user['id'])
            return redirect(url_for('dashboard.index'))
        flash('Invalid username or password.', 'error')

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/setup', methods=['GET', 'POST'])
def setup():
    if app_has_registered_users():
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not username or not email or not password:
            flash('All fields are required.', 'error')
        elif password != confirm:
            flash('Passwords do not match.', 'error')
        elif len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
        else:
            pw_hash = hash_password(password)
            uid = execute_returning(
                'INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s) RETURNING id',
                (username, email, pw_hash, 'admin')
            )
            login_user(uid)
            flash('Admin account created. Welcome to Specci!', 'success')
            return redirect(url_for('dashboard.index'))

    return render_template('auth/setup.html')
