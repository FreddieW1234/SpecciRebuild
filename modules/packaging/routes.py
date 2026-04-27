from flask import render_template, request, redirect, url_for, flash
from modules.packaging import bp
from core.decorators import login_required
from core.db import query_one, query_all, execute, execute_returning

PACKAGING_TYPES = [
    'Bag', 'Box', 'Carton', 'Case', 'Tray', 'Pot', 'Jar', 'Tin',
    'Sachet', 'Pouch', 'Wrap', 'Label', 'Film', 'Insert', 'Divider', 'Pallet', 'Other'
]
MATERIAL_CATEGORIES = [
    'Plastic', 'Paper', 'Cardboard', 'Foil', 'Glass', 'Metal', 'Composite', 'Wood', 'Fabric', 'Other'
]
STATUSES = ['Active', 'Draft', 'Discontinued', 'Under Review']
CURRENCIES = ['GBP', 'EUR', 'USD']


def _get_all(search=None):
    sql = 'SELECT * FROM packaging_components WHERE 1=1'
    params = []
    if search:
        sql += ' AND (internal_description ILIKE %s OR ba_code ILIKE %s)'
        params += [f'%{search}%', f'%{search}%']
    sql += ' ORDER BY internal_description'
    return query_all(sql, params or None)


def _get(pkg_id):
    return query_one('SELECT * FROM packaging_components WHERE id = %s', (pkg_id,))


def _apply_update(pkg_id, data):
    fields = [
        'ba_code', 'internal_description', 'supplier_product_code',
        'supplier_description', 'status', 'packaging_type', 'material_category',
        'specific_material', 'length_mm', 'width_mm', 'height_mm', 'diameter_mm',
        'capacity_volume', 'packaging_weight_grams', 'colour',
        'food_contact_approved', 'temp_range_min', 'temp_range_max',
        'recyclable', 'compostable', 'printing_labelling', 'printing_description',
        'barcode_type', 'storage_conditions', 'packaging_shelf_life_months',
        'cost_per_unit', 'currency', 'minimum_order_quantity', 'lead_time_days', 'notes',
    ]
    float_fields = {'length_mm', 'width_mm', 'height_mm', 'diameter_mm',
                    'packaging_weight_grams', 'temp_range_min', 'temp_range_max',
                    'cost_per_unit', 'packaging_shelf_life_months'}
    int_fields = {'supplier_id', 'minimum_order_quantity', 'lead_time_days'}
    bool_fields = {'food_contact_approved', 'recyclable', 'compostable', 'printing_labelling'}

    def coerce(k, v):
        if not v:
            return None
        if k in float_fields:
            try:
                return float(v)
            except (TypeError, ValueError):
                return None
        if k in int_fields:
            try:
                return int(v)
            except (TypeError, ValueError):
                return None
        if k in bool_fields:
            return v in ('on', 'true', '1', 'yes')
        return v

    # Handle supplier_id separately (not in fields list above)
    extra = {}
    if data.get('supplier_id'):
        try:
            extra['supplier_id'] = int(data['supplier_id'])
        except (TypeError, ValueError):
            extra['supplier_id'] = None

    all_fields = fields + list(extra.keys())
    values = [coerce(k, data.get(k)) for k in fields] + list(extra.values())
    set_clause = ', '.join(f'{k}=%s' for k in all_fields)
    execute(f'UPDATE packaging_components SET {set_clause} WHERE id=%s', values + [pkg_id])


@bp.route('/')
@login_required
def index():
    search = request.args.get('q', '').strip()
    items = _get_all(search=search or None)
    return render_template('packaging/index.html', items=items, search=search,
                           statuses=STATUSES)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    suppliers = query_all('SELECT id, supplier_name FROM suppliers ORDER BY supplier_name')
    if request.method == 'POST':
        data = request.form.to_dict()
        if not data.get('internal_description'):
            flash('Description is required.', 'error')
            return render_template('packaging/form.html', pkg={}, is_new=True,
                                   packaging_types=PACKAGING_TYPES, material_categories=MATERIAL_CATEGORIES,
                                   statuses=STATUSES, currencies=CURRENCIES, suppliers=suppliers)
        pkg_id = execute_returning('''
            INSERT INTO packaging_components (ba_code, internal_description, status, packaging_type)
            VALUES (%s, %s, %s, %s) RETURNING id
        ''', (
            data.get('ba_code') or None,
            data.get('internal_description'),
            data.get('status', 'Draft'),
            data.get('packaging_type') or None,
        ))
        _apply_update(pkg_id, data)
        flash('Packaging component created.', 'success')
        return redirect(url_for('packaging.detail', id=pkg_id))
    return render_template('packaging/form.html', pkg={}, is_new=True,
                           packaging_types=PACKAGING_TYPES, material_categories=MATERIAL_CATEGORIES,
                           statuses=STATUSES, currencies=CURRENCIES, suppliers=suppliers)


@bp.route('/<int:id>')
@login_required
def detail(id):
    pkg = _get(id)
    if not pkg:
        flash('Packaging component not found.', 'error')
        return redirect(url_for('packaging.index'))
    suppliers = query_all('SELECT id, supplier_name FROM suppliers ORDER BY supplier_name')
    return render_template('packaging/detail.html', pkg=pkg, suppliers=suppliers)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    pkg = _get(id)
    if not pkg:
        flash('Packaging component not found.', 'error')
        return redirect(url_for('packaging.index'))
    suppliers = query_all('SELECT id, supplier_name FROM suppliers ORDER BY supplier_name')
    if request.method == 'POST':
        data = request.form.to_dict()
        _apply_update(id, data)
        flash('Packaging component updated.', 'success')
        return redirect(url_for('packaging.detail', id=id))
    return render_template('packaging/form.html', pkg=pkg, is_new=False,
                           packaging_types=PACKAGING_TYPES, material_categories=MATERIAL_CATEGORIES,
                           statuses=STATUSES, currencies=CURRENCIES, suppliers=suppliers)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    execute('DELETE FROM packaging_components WHERE id = %s', (id,))
    flash('Packaging component deleted.', 'success')
    return redirect(url_for('packaging.index'))
