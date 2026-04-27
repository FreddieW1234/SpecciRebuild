import json
from flask import render_template, request, redirect, url_for, flash, g, session
from modules.finished_products import bp
from modules.finished_products.models import (
    get_all_finished_products, get_deleted_finished_products,
    get_finished_product, create_finished_product,
    update_finished_product, update_sensory, update_suitability,
    soft_delete_finished_product, restore_finished_product,
    get_recipe_items, add_recipe_item, delete_recipe_item,
    get_linked_equipment, link_equipment, unlink_equipment,
)
from core.decorators import login_required
from core.db import query_all, query_one, execute


MANUFACTURERS = ['Michton Ltd', 'Bakeart (UK) Ltd', 'Universal']
STATUSES = ['Draft', 'Active', 'Under Review', 'Archived']


def _active_company_id():
    return session.get('active_company_id', 1)


def _invalidate_explosion_cache(fp_id):
    """Delete the explosion cache row so it will be recalculated on demand."""
    try:
        execute('DELETE FROM finished_product_explosion_cache WHERE finished_product_id = %s', (fp_id,))
    except Exception:
        pass


@bp.route('/')
@login_required
def index():
    search = request.args.get('q', '').strip()
    company_id = _active_company_id()
    products = get_all_finished_products(company_id, search=search or None)
    return render_template('finished_products/index.html',
                           products=products, search=search,
                           statuses=STATUSES)


@bp.route('/bin')
@login_required
def bin_view():
    company_id = _active_company_id()
    products = get_deleted_finished_products(company_id)
    return render_template('finished_products/bin.html', products=products)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    company_id = _active_company_id()
    if request.method == 'POST':
        data = request.form.to_dict()
        if not data.get('name'):
            flash('Product name is required.', 'error')
            return render_template('finished_products/form.html', fp={},
                                   is_new=True, manufacturers=MANUFACTURERS, statuses=STATUSES)
        fp_id = create_finished_product(data, company_id)
        flash('Finished product created.', 'success')
        return redirect(url_for('finished_products.detail', id=fp_id))
    return render_template('finished_products/form.html', fp={},
                           is_new=True, manufacturers=MANUFACTURERS, statuses=STATUSES)


@bp.route('/<int:id>')
@login_required
def detail(id):
    fp = get_finished_product(id)
    if not fp:
        flash('Product not found.', 'error')
        return redirect(url_for('finished_products.index'))
    recipe = get_recipe_items(id)
    linked_eq = get_linked_equipment(id)

    # Components available for recipe (exclude Finished Product type)
    all_components = query_all(
        "SELECT id, code, name FROM components WHERE component_type != 'Finished Product' ORDER BY name"
    )
    # Other finished products available as recipe ingredients (exclude self)
    all_fps_for_recipe = query_all(
        'SELECT id, ba_code, name FROM finished_products WHERE deleted_at IS NULL AND id != %s ORDER BY name',
        (id,)
    )
    all_equipment = query_all(
        'SELECT id, tool_number, description, size_raw FROM equipment WHERE is_active = TRUE ORDER BY tool_number'
    )

    # Parse suitability_data JSON
    suitability = {}
    if fp.get('suitability_data'):
        try:
            sd = fp['suitability_data']
            suitability = json.loads(sd) if isinstance(sd, str) else sd
        except (ValueError, TypeError):
            suitability = {}

    # Explosion cache
    cache = query_one(
        'SELECT * FROM finished_product_explosion_cache WHERE finished_product_id = %s', (id,)
    )
    explosion_rows = []
    allergen_summary = {}
    if cache:
        try:
            explosion_rows = json.loads(cache['explosion_data']) if cache.get('explosion_data') else []
        except (ValueError, TypeError):
            explosion_rows = []
        try:
            allergen_summary = json.loads(cache['allergen_summary']) if cache.get('allergen_summary') else {}
        except (ValueError, TypeError):
            allergen_summary = {}

    # Manual allergen overrides
    fp_allergen_rows = query_all(
        'SELECT allergen_name, manual_status, notes FROM finished_product_allergens WHERE finished_product_id = %s',
        (id,)
    )
    allergen_overrides = {r['allergen_name']: r for r in fp_allergen_rows}

    # Net weight for direct recipe % calculation
    net_weight = float(fp.get('net_weight_grams') or 0)

    # Build direct recipe rows with percentage
    recipe_display = []
    for item in recipe:
        g = float(item.get('grams_per_unit') or 0)
        pct = round(g / net_weight * 100, 2) if net_weight > 0 else None
        recipe_display.append({**item, 'percent': pct})

    from core.reference_data import ALLERGENS as ALLERGEN_LIST
    total_explosion_grams = sum(r.get('grams', 0) for r in explosion_rows)

    return render_template('finished_products/detail.html',
                           fp=fp, recipe=recipe_display, linked_eq=linked_eq,
                           all_components=all_components, all_fps_for_recipe=all_fps_for_recipe,
                           all_equipment=all_equipment,
                           suitability=suitability,
                           explosion_rows=explosion_rows,
                           allergen_summary=allergen_summary,
                           allergen_overrides=allergen_overrides,
                           allergens=ALLERGEN_LIST,
                           explosion_cache=cache,
                           total_explosion_grams=total_explosion_grams,
                           net_weight=net_weight,
                           manufacturers=MANUFACTURERS, statuses=STATUSES)


@bp.route('/<int:id>/edit', methods=['POST'])
@login_required
def edit(id):
    fp = get_finished_product(id)
    if not fp:
        flash('Product not found.', 'error')
        return redirect(url_for('finished_products.index'))
    data = request.form.to_dict()
    if not data.get('name'):
        flash('Product name is required.', 'error')
        return redirect(url_for('finished_products.detail', id=id) + '#overview')
    update_finished_product(id, data)
    _invalidate_explosion_cache(id)
    flash('Product updated.', 'success')
    return redirect(url_for('finished_products.detail', id=id) + '#overview')


@bp.route('/<int:id>/sensory', methods=['POST'])
@login_required
def save_sensory(id):
    if not get_finished_product(id):
        flash('Product not found.', 'error')
        return redirect(url_for('finished_products.index'))
    update_sensory(id, request.form.to_dict())
    flash('Sensory data saved.', 'success')
    return redirect(url_for('finished_products.detail', id=id) + '#sensory')


@bp.route('/<int:id>/suitability', methods=['POST'])
@login_required
def save_suitability(id):
    if not get_finished_product(id):
        flash('Product not found.', 'error')
        return redirect(url_for('finished_products.index'))
    # Collect all suitability checkboxes/fields into a JSON blob
    data = request.form.to_dict()
    update_suitability(id, json.dumps(data))
    flash('Suitability saved.', 'success')
    return redirect(url_for('finished_products.detail', id=id) + '#suitability')


@bp.route('/<int:id>/recipe', methods=['POST'])
@login_required
def add_recipe(id):
    if not get_finished_product(id):
        flash('Product not found.', 'error')
        return redirect(url_for('finished_products.index'))
    ingredient_id = request.form.get('ingredient_id')
    item_type = request.form.get('item_type', 'Component')
    grams = request.form.get('grams_per_unit')
    if not ingredient_id:
        flash('Select an ingredient.', 'error')
        return redirect(url_for('finished_products.detail', id=id) + '#recipe')
    # Validate item_type
    if item_type not in ('Component', 'FinishedProduct'):
        item_type = 'Component'
    try:
        grams_val = float(grams) if grams else None
    except ValueError:
        grams_val = None
    add_recipe_item(id, int(ingredient_id), item_type, grams_val)
    # Invalidate explosion cache
    _invalidate_explosion_cache(id)
    flash('Recipe item added.', 'success')
    return redirect(url_for('finished_products.detail', id=id) + '#recipe')


@bp.route('/<int:id>/recipe/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_recipe(id, item_id):
    delete_recipe_item(item_id)
    _invalidate_explosion_cache(id)
    flash('Recipe item removed.', 'success')
    return redirect(url_for('finished_products.detail', id=id) + '#recipe')


@bp.route('/<int:id>/equipment', methods=['POST'])
@login_required
def add_equipment(id):
    if not get_finished_product(id):
        flash('Product not found.', 'error')
        return redirect(url_for('finished_products.index'))
    equipment_id = request.form.get('equipment_id')
    if not equipment_id:
        flash('Select a tool head.', 'error')
        return redirect(url_for('finished_products.detail', id=id) + '#equipment')
    link_equipment(id, int(equipment_id))
    flash('Tool head linked.', 'success')
    return redirect(url_for('finished_products.detail', id=id) + '#equipment')


@bp.route('/<int:id>/equipment/<int:eq_id>/delete', methods=['POST'])
@login_required
def remove_equipment(id, eq_id):
    unlink_equipment(id, eq_id)
    flash('Tool head removed.', 'success')
    return redirect(url_for('finished_products.detail', id=id) + '#equipment')


@bp.route('/<int:id>/explosion', methods=['POST'])
@login_required
def recalculate_explosion(id):
    fp = get_finished_product(id)
    if not fp:
        flash('Product not found.', 'error')
        return redirect(url_for('finished_products.index'))
    from modules.finished_products.explosion import update_explosion_cache
    update_explosion_cache(id)
    flash('Recipe explosion recalculated.', 'success')
    return redirect(url_for('finished_products.detail', id=id) + '#recipe')


@bp.route('/<int:id>/allergens', methods=['POST'])
@login_required
def save_allergens(id):
    if not get_finished_product(id):
        flash('Product not found.', 'error')
        return redirect(url_for('finished_products.index'))
    from core.reference_data import ALLERGENS
    for allergen_name in ALLERGENS:
        manual_status = request.form.get(f'manual_{allergen_name}', '').strip() or None
        notes = request.form.get(f'notes_{allergen_name}', '').strip() or None
        try:
            execute('''
                INSERT INTO finished_product_allergens
                    (finished_product_id, allergen_name, manual_status, notes)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (finished_product_id, allergen_name)
                DO UPDATE SET manual_status = EXCLUDED.manual_status,
                              notes = EXCLUDED.notes
            ''', (id, allergen_name, manual_status, notes))
        except Exception:
            pass
    flash('Allergen overrides saved.', 'success')
    return redirect(url_for('finished_products.detail', id=id) + '#allergens')


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    fp = get_finished_product(id)
    if not fp:
        flash('Product not found.', 'error')
        return redirect(url_for('finished_products.index'))
    soft_delete_finished_product(id, g.current_user['username'])
    flash(f'"{fp["name"]}" moved to bin.', 'success')
    return redirect(url_for('finished_products.index'))


@bp.route('/<int:id>/restore', methods=['POST'])
@login_required
def restore(id):
    fp = get_finished_product(id)
    if not fp:
        flash('Product not found.', 'error')
        return redirect(url_for('finished_products.bin_view'))
    restore_finished_product(id)
    flash(f'"{fp["name"]}" restored.', 'success')
    return redirect(url_for('finished_products.bin_view'))
