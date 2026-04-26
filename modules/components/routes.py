from flask import render_template, request, redirect, url_for, flash, g
from modules.components import bp
from modules.components.models import (
    get_all_components, get_component, create_component, update_component, delete_component,
    get_spec, upsert_spec,
    get_constituents, upsert_constituents,
    get_allergens, upsert_allergens,
    get_storage, upsert_storage,
    get_packaging, upsert_packaging,
    get_analytical, upsert_analytical,
    get_micro, upsert_micro,
    get_additives, upsert_additives,
    get_palm, upsert_palm,
)
from core.decorators import login_required
from core.reference_data import (
    COMPONENT_TYPES, PRODUCT_LEVELS, COMPONENT_STATUSES, ALLERGENS, ALLERGEN_STATUSES,
    GMO_STATUS_OPTIONS, PALM_OIL_STATUS_OPTIONS, CERTIFICATION_OPTIONS,
    PACKAGING_LEVELS, COUNTRIES, NUTRITION_FIELDS, MICRO_TEST_NAMES,
)
from core.db import query_all


def _parse_table_rows(form, prefix, fields):
    """Extract indexed rows from a form submission like prefix_0_field, prefix_1_field…"""
    rows = {}
    for key, value in form.items():
        if not key.startswith(prefix + '_'):
            continue
        rest = key[len(prefix) + 1:]
        parts = rest.split('_', 1)
        if len(parts) != 2:
            continue
        try:
            idx = int(parts[0])
        except ValueError:
            continue
        field = parts[1]
        if field not in fields:
            continue
        if idx not in rows:
            rows[idx] = {}
        rows[idx][field] = value
    return [rows[i] for i in sorted(rows)]


@bp.route('/')
@login_required
def index():
    search = request.args.get('q', '').strip()
    type_filter = request.args.get('type', '').strip()
    status_filter = request.args.get('status', '').strip()
    components = get_all_components(
        search=search or None,
        type_filter=type_filter or None,
        status_filter=status_filter or None,
    )
    return render_template('components/index.html', components=components,
                           search=search, type_filter=type_filter, status_filter=status_filter,
                           component_types=COMPONENT_TYPES, statuses=COMPONENT_STATUSES)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        data = request.form.to_dict()
        if not data.get('name') or not data.get('component_type'):
            flash('Name and type are required.', 'error')
            return render_template('components/form.html', component=data, is_new=True,
                                   component_types=COMPONENT_TYPES, product_levels=PRODUCT_LEVELS,
                                   statuses=COMPONENT_STATUSES)
        cid = create_component(data)
        flash('Component created.', 'success')
        return redirect(url_for('components.detail', id=cid))
    return render_template('components/form.html', component={}, is_new=True,
                           component_types=COMPONENT_TYPES, product_levels=PRODUCT_LEVELS,
                           statuses=COMPONENT_STATUSES)


@bp.route('/<int:id>')
@login_required
def detail(id):
    component = get_component(id)
    if not component:
        flash('Component not found.', 'error')
        return redirect(url_for('components.index'))
    spec = get_spec(id) or {}
    constituents = get_constituents(id)
    allergens_list = get_allergens(id)
    allergen_map = {a['allergen_name']: a for a in allergens_list}
    storage = get_storage(id) or {}
    packaging = get_packaging(id)
    analytical = get_analytical(id)
    micro = get_micro(id)
    additives = get_additives(id)
    palm = get_palm(id) or {}
    all_suppliers = query_all('SELECT id, supplier_name, supplier_code FROM suppliers ORDER BY supplier_name')
    return render_template('components/detail.html',
                           component=component, spec=spec,
                           constituents=constituents, allergens=ALLERGENS,
                           allergen_map=allergen_map, allergen_statuses=ALLERGEN_STATUSES,
                           storage=storage, packaging=packaging, packaging_levels=PACKAGING_LEVELS,
                           analytical=analytical, micro=micro, micro_test_names=MICRO_TEST_NAMES,
                           additives=additives, palm=palm,
                           gmo_options=GMO_STATUS_OPTIONS, palm_options=PALM_OIL_STATUS_OPTIONS,
                           cert_options=CERTIFICATION_OPTIONS, countries=COUNTRIES,
                           nutrition_fields=NUTRITION_FIELDS, all_suppliers=all_suppliers,
                           component_types=COMPONENT_TYPES, product_levels=PRODUCT_LEVELS,
                           statuses=COMPONENT_STATUSES)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    component = get_component(id)
    if not component:
        flash('Component not found.', 'error')
        return redirect(url_for('components.index'))
    if request.method == 'POST':
        data = request.form.to_dict()
        if not data.get('name') or not data.get('component_type'):
            flash('Name and type are required.', 'error')
            return render_template('components/form.html', component=data, is_new=False,
                                   component_types=COMPONENT_TYPES, product_levels=PRODUCT_LEVELS,
                                   statuses=COMPONENT_STATUSES)
        update_component(id, data)
        flash('Component updated.', 'success')
        return redirect(url_for('components.detail', id=id))
    return render_template('components/form.html', component=component, is_new=False,
                           component_types=COMPONENT_TYPES, product_levels=PRODUCT_LEVELS,
                           statuses=COMPONENT_STATUSES)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    delete_component(id)
    flash('Component deleted.', 'success')
    return redirect(url_for('components.index'))


@bp.route('/<int:id>/spec', methods=['POST'])
@login_required
def save_spec(id):
    if not get_component(id):
        flash('Component not found.', 'error')
        return redirect(url_for('components.index'))
    upsert_spec(id, request.form.to_dict())
    flash('Specification saved.', 'success')
    return redirect(url_for('components.detail', id=id) + '#spec')


@bp.route('/<int:id>/constituents', methods=['POST'])
@login_required
def save_constituents(id):
    if not get_component(id):
        flash('Component not found.', 'error')
        return redirect(url_for('components.index'))
    fields = [
        'constituent_name', 'constituent_ba_code', 'constituent_level', 'composition_percent',
        'declare_on_label', 'country_of_origin', 'country_of_processing', 'country_of_manufacture',
        'supplier_details', 'manufacturer_details', 'notes', 'e_number',
        'allergen_milk', 'allergen_gluten', 'allergen_nuts', 'allergen_soya',
        'allergen_eggs', 'allergen_fish', 'allergen_crustaceans', 'allergen_celery',
        'allergen_mustard', 'allergen_sesame', 'allergen_sulphites', 'allergen_lupin',
        'allergen_molluscs', 'batch_lot_traceable', 'batch_lot_code',
    ]
    rows = _parse_table_rows(request.form, 'row', fields)
    upsert_constituents(id, rows)
    flash('Constituents saved.', 'success')
    return redirect(url_for('components.detail', id=id) + '#constituents')


@bp.route('/<int:id>/allergens', methods=['POST'])
@login_required
def save_allergens(id):
    if not get_component(id):
        flash('Component not found.', 'error')
        return redirect(url_for('components.index'))
    allergen_data = {}
    for allergen in ALLERGENS:
        status = request.form.get(f'allergen_{allergen}')
        notes = request.form.get(f'notes_{allergen}', '')
        if status:
            allergen_data[allergen] = status
            allergen_data[f'{allergen}__notes'] = notes
    upsert_allergens(id, allergen_data)
    flash('Allergen status saved.', 'success')
    return redirect(url_for('components.detail', id=id) + '#allergens')


@bp.route('/<int:id>/storage', methods=['POST'])
@login_required
def save_storage(id):
    if not get_component(id):
        flash('Component not found.', 'error')
        return redirect(url_for('components.index'))
    upsert_storage(id, request.form.to_dict())
    flash('Storage conditions saved.', 'success')
    return redirect(url_for('components.detail', id=id) + '#storage')


@bp.route('/<int:id>/packaging', methods=['POST'])
@login_required
def save_packaging(id):
    if not get_component(id):
        flash('Component not found.', 'error')
        return redirect(url_for('components.index'))
    fields = [
        'packaging_level', 'description_material_type', 'food_contact', 'food_contact_compliant',
        'external_dimensions_l', 'external_dimensions_w', 'external_dimensions_h',
        'empty_weight_g', 'filled_weight_g', 'colour_code', 'barcode_code',
        'units_per_next_level', 'recyclable', 'supplier_origin', 'other_features', 'comments_notes',
    ]
    rows = _parse_table_rows(request.form, 'pkg', fields)
    upsert_packaging(id, rows)
    flash('Packaging saved.', 'success')
    return redirect(url_for('components.detail', id=id) + '#packaging')


@bp.route('/<int:id>/analytical', methods=['POST'])
@login_required
def save_analytical(id):
    if not get_component(id):
        flash('Component not found.', 'error')
        return redirect(url_for('components.index'))
    fields = ['parameter_name', 'target_value', 'acceptable_range', 'typical_value',
              'method_of_analysis', 'qc_frequency']
    rows = _parse_table_rows(request.form, 'ap', fields)
    upsert_analytical(id, rows)
    flash('Analytical parameters saved.', 'success')
    return redirect(url_for('components.detail', id=id) + '#analytical')


@bp.route('/<int:id>/micro', methods=['POST'])
@login_required
def save_micro(id):
    if not get_component(id):
        flash('Component not found.', 'error')
        return redirect(url_for('components.index'))
    fields = ['test_name', 'status', 'notes', 'test_method', 'positive_release']
    rows = _parse_table_rows(request.form, 'mt', fields)
    upsert_micro(id, rows)
    flash('Micro tests saved.', 'success')
    return redirect(url_for('components.detail', id=id) + '#micro')


@bp.route('/<int:id>/additives', methods=['POST'])
@login_required
def save_additives(id):
    if not get_component(id):
        flash('Component not found.', 'error')
        return redirect(url_for('components.index'))
    fields = ['legal_name', 'e_number', 'function', 'natural_artificial', 'level_in_product']
    rows = _parse_table_rows(request.form, 'add', fields)
    upsert_additives(id, rows)
    flash('Additives saved.', 'success')
    return redirect(url_for('components.detail', id=id) + '#additives')


@bp.route('/<int:id>/palm', methods=['POST'])
@login_required
def save_palm(id):
    if not get_component(id):
        flash('Component not found.', 'error')
        return redirect(url_for('components.index'))
    upsert_palm(id, request.form.to_dict())
    flash('Palm oil details saved.', 'success')
    return redirect(url_for('components.detail', id=id) + '#palm')
