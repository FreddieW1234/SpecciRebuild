from functools import wraps
from flask import redirect, url_for, g


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.get('current_user'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated
