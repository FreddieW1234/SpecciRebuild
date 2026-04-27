from flask import render_template, request, redirect, url_for, flash
from modules.product_templates import bp
from core.decorators import login_required
from core.db import query_one, query_all, execute, execute_returning


def _get_all():
    return query_all('SELECT * FROM product_templates ORDER BY name')


def _get(template_id):
    return query_one('SELECT * FROM product_templates WHERE id = %s', (template_id,))


@bp.route('/')
@login_required
def index():
    templates = _get_all()
    return render_template('product_templates/index.html', templates=templates)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        data = request.form.to_dict()
        if not data.get('name'):
            flash('Template name is required.', 'error')
            return render_template('product_templates/form.html', tmpl={}, is_new=True)
        tid = execute_returning('''
            INSERT INTO product_templates (code, name, description, is_active)
            VALUES (%s, %s, %s, %s) RETURNING id
        ''', (
            data.get('code') or None,
            data.get('name'),
            data.get('description') or None,
            True,
        ))
        flash('Template created.', 'success')
        return redirect(url_for('product_templates.detail', id=tid))
    return render_template('product_templates/form.html', tmpl={}, is_new=True)


@bp.route('/<int:id>')
@login_required
def detail(id):
    tmpl = _get(id)
    if not tmpl:
        flash('Template not found.', 'error')
        return redirect(url_for('product_templates.index'))
    return render_template('product_templates/detail.html', tmpl=tmpl)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    tmpl = _get(id)
    if not tmpl:
        flash('Template not found.', 'error')
        return redirect(url_for('product_templates.index'))
    if request.method == 'POST':
        data = request.form.to_dict()
        if not data.get('name'):
            flash('Template name is required.', 'error')
            return render_template('product_templates/form.html', tmpl=data, is_new=False)

        # Build SET clause dynamically from all form fields that exist as columns
        allowed_fields = [
            'code', 'name', 'description', 'is_active',
            'v_storage_conditions', 'w_shelf_life_format',
            'free_from_gluten', 'free_from_dairy', 'free_from_nuts',
            'free_from_soya', 'free_from_eggs',
            'suitable_vegetarian', 'suitable_vegan', 'suitable_halal', 'suitable_kosher',
        ]
        updates = {}
        for field in allowed_fields:
            if field in data:
                if field == 'is_active':
                    updates[field] = data[field] == 'on' or data[field] == 'true'
                else:
                    updates[field] = data[field] or None

        if updates:
            set_clause = ', '.join(f'{k}=%s' for k in updates)
            execute(f'UPDATE product_templates SET {set_clause} WHERE id=%s',
                    list(updates.values()) + [id])
        flash('Template saved.', 'success')
        return redirect(url_for('product_templates.detail', id=id))
    return render_template('product_templates/form.html', tmpl=tmpl, is_new=False)
