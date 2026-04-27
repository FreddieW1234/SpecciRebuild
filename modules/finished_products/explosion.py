"""
Finished Product recipe explosion engine.

explode_finished_product(fp_id)  → full BOM breakdown to raw materials
calculate_allergens_from_explosion(rows) → allergen status per allergen
update_explosion_cache(fp_id)    → run explosion + persist results
"""
import json
from core.db import query_one, query_all, execute

# Map from ALLERGENS list names to component_constituents boolean columns
CONSTITUENT_ALLERGEN_MAP = {
    'Celery': 'allergen_celery',
    'Cereals containing gluten': 'allergen_gluten',
    'Crustaceans': 'allergen_crustaceans',
    'Eggs': 'allergen_eggs',
    'Fish': 'allergen_fish',
    'Lupin': 'allergen_lupin',
    'Milk': 'allergen_milk',
    'Molluscs': 'allergen_molluscs',
    'Mustard': 'allergen_mustard',
    'Nuts': 'allergen_nuts',
    'Sesame seeds': 'allergen_sesame',
    'Soya': 'allergen_soya',
    'Sulphur dioxide and sulphites': 'allergen_sulphites',
}

ALLERGENS = [
    'Celery', 'Cereals containing gluten', 'Crustaceans', 'Eggs', 'Fish',
    'Lupin', 'Milk', 'Molluscs', 'Mustard', 'Nuts', 'Peanuts',
    'Sesame seeds', 'Soya', 'Sulphur dioxide and sulphites',
]


def _get_component_allergen_statuses(component_id):
    """Return dict allergen_name → status from component_allergens."""
    rows = query_all(
        'SELECT allergen_name, status FROM component_allergens WHERE component_id = %s',
        (component_id,)
    )
    return {r['allergen_name']: r['status'] for r in rows}


def _explode_recursive(fp_id, scale, visited_path, path_label, rows_out, circular_refs):
    """
    Recursively expand recipe items into raw-material rows.

    scale        — multiplier: 1.0 means one unit of this FP
    visited_path — frozenset of fp_ids currently on the call stack (cycle detection)
    path_label   — human-readable chain so far (e.g. "Sprinkle Mix")
    rows_out     — accumulator list, mutated in place
    circular_refs— list of circular-ref descriptions, mutated in place
    """
    recipe = query_all('''
        SELECT ri.*,
            COALESCE(c.name, fp2.name) AS item_name,
            COALESCE(c.code, fp2.ba_code) AS item_code,
            fp2.net_weight_grams AS fp_net_weight
        FROM finished_product_recipe_items ri
        LEFT JOIN components c
            ON c.id = ri.item_id
            AND ri.item_type IN ('component', 'Component')
        LEFT JOIN finished_products fp2
            ON fp2.id = ri.item_id
            AND ri.item_type = 'FinishedProduct'
        WHERE ri.finished_product_id = %s
        ORDER BY ri.id
    ''', (fp_id,))

    for item in recipe:
        grams = float(item['grams_per_unit'] or 0) * scale
        item_type = item['item_type']
        item_name = item['item_name'] or f'Item #{item["item_id"]}'
        item_code = item['item_code'] or ''
        item_path = f'{path_label} → {item_name}' if path_label else item_name

        if item_type in ('component', 'Component'):
            component_id = item['item_id']

            # Check for constituent breakdown
            constituents = query_all(
                'SELECT * FROM component_constituents WHERE component_id = %s ORDER BY id',
                (component_id,)
            )

            if constituents:
                total_pct = sum(float(c['composition_percent'] or 0) for c in constituents)
                if total_pct == 0:
                    total_pct = 100.0

                for const in constituents:
                    pct = float(const['composition_percent'] or 0) / total_pct
                    const_grams = grams * pct
                    const_path = f'{item_path} → {const["constituent_name"]}'

                    # Build allergen flags from constituent boolean columns
                    a_contains = {}
                    for allergen, col in CONSTITUENT_ALLERGEN_MAP.items():
                        if const.get(col):
                            a_contains[allergen] = True

                    rows_out.append({
                        'name': const['constituent_name'] or '',
                        'ba_code': const['constituent_ba_code'] or '',
                        'grams': const_grams,
                        'path': const_path,
                        'level': 2,
                        'allergen_contains': a_contains,
                        'allergen_may_contain': {},
                    })
            else:
                # No constituents — treat as raw material
                comp_statuses = _get_component_allergen_statuses(component_id)
                a_contains = {a: True for a, s in comp_statuses.items() if s == 'Contains'}
                a_may = {a: True for a, s in comp_statuses.items() if s == 'May Contain'}

                rows_out.append({
                    'name': item_name,
                    'ba_code': item_code,
                    'grams': grams,
                    'path': item_path,
                    'level': 1,
                    'allergen_contains': a_contains,
                    'allergen_may_contain': a_may,
                })

        elif item_type == 'FinishedProduct':
            sub_fp_id = item['item_id']

            if sub_fp_id in visited_path:
                circular_refs.append(
                    f'"{item_name}" (id={sub_fp_id}) is already in the chain: {item_path}'
                )
                continue

            sub_net = float(item['fp_net_weight'] or 0)
            if sub_net <= 0:
                # No net weight set — can't scale; treat as one unit
                sub_net = 1.0

            sub_scale = grams / sub_net
            new_visited = visited_path | {sub_fp_id}
            _explode_recursive(sub_fp_id, sub_scale, new_visited, item_path, rows_out, circular_refs)


def explode_finished_product(fp_id, visited=None):
    """
    Recursively explode a finished product into its raw materials.

    Returns:
      {
        'rows': [{'name', 'ba_code', 'grams', 'path', 'level',
                  'allergen_contains', 'allergen_may_contain', 'percent'}],
        'has_circular_ref': bool,
        'circular_ref_detail': str | None,
        'total_grams': float,
        'net_weight': float,
      }
    """
    seed = set(visited) if visited else set()
    visited_path = frozenset(seed | {fp_id})

    rows_out = []
    circular_refs = []

    _explode_recursive(fp_id, 1.0, visited_path, '', rows_out, circular_refs)

    # Merge duplicate raw materials (same name) — sum grams, union allergens
    merged = {}
    for row in rows_out:
        key = row['name'] or f'__unnamed_{id(row)}'
        if key in merged:
            merged[key]['grams'] += row['grams']
            for a in row['allergen_contains']:
                merged[key]['allergen_contains'][a] = True
            for a in row['allergen_may_contain']:
                merged[key]['allergen_may_contain'][a] = True
        else:
            merged[key] = {
                'name': row['name'],
                'ba_code': row['ba_code'],
                'grams': row['grams'],
                'path': row['path'],
                'level': row['level'],
                'allergen_contains': dict(row['allergen_contains']),
                'allergen_may_contain': dict(row['allergen_may_contain']),
            }

    final_rows = list(merged.values())
    total_grams = sum(r['grams'] for r in final_rows)

    # Net weight for % calculation
    fp = query_one('SELECT net_weight_grams FROM finished_products WHERE id = %s', (fp_id,))
    net_weight = float(fp['net_weight_grams'] or 0) if fp and fp.get('net_weight_grams') else 0

    for row in final_rows:
        if net_weight > 0:
            row['percent'] = round(row['grams'] / net_weight * 100, 2)
        else:
            row['percent'] = None

    has_circular = bool(circular_refs)
    circular_detail = '; '.join(circular_refs) if circular_refs else None

    return {
        'rows': final_rows,
        'has_circular_ref': has_circular,
        'circular_ref_detail': circular_detail,
        'total_grams': total_grams,
        'net_weight': net_weight,
    }


def calculate_allergens_from_explosion(explosion_rows):
    """
    Calculate allergen status from explosion rows.
    Returns dict: allergen_name → 'Contains' | 'May Contain' | 'Free From'
    """
    result = {}
    for allergen in ALLERGENS:
        status = 'Free From'
        for row in explosion_rows:
            if row.get('allergen_contains', {}).get(allergen):
                status = 'Contains'
                break
            if row.get('allergen_may_contain', {}).get(allergen):
                status = 'May Contain'
        result[allergen] = status
    return result


def update_explosion_cache(fp_id):
    """
    Run explosion, persist to finished_product_explosion_cache,
    update has_circular_ref flag on finished_products, and update
    auto-calculated allergens in finished_product_allergens.
    """
    try:
        result = explode_finished_product(fp_id)
    except Exception:
        return  # Don't crash the app on bad data

    allergen_summary = calculate_allergens_from_explosion(result['rows'])

    # Serialize rows for storage (strip per-row allergen dicts — they're in allergen_summary)
    storable_rows = []
    for row in result['rows']:
        storable_rows.append({
            'name': row['name'],
            'ba_code': row['ba_code'],
            'grams': round(row['grams'], 4),
            'path': row['path'],
            'level': row['level'],
            'percent': row.get('percent'),
        })

    explosion_json = json.dumps(storable_rows)
    allergen_json = json.dumps(allergen_summary)

    # Upsert cache row
    existing = query_one(
        'SELECT finished_product_id FROM finished_product_explosion_cache WHERE finished_product_id = %s',
        (fp_id,)
    )
    if existing:
        execute('''
            UPDATE finished_product_explosion_cache
            SET explosion_data = %s, allergen_summary = %s, calculated_at = NOW()
            WHERE finished_product_id = %s
        ''', (explosion_json, allergen_json, fp_id))
    else:
        execute('''
            INSERT INTO finished_product_explosion_cache
                (finished_product_id, explosion_data, allergen_summary, calculated_at)
            VALUES (%s, %s, %s, NOW())
        ''', (fp_id, explosion_json, allergen_json))

    # Update circular ref flag on the finished product
    execute('''
        UPDATE finished_products
        SET has_circular_ref = %s, circular_ref_detail = %s
        WHERE id = %s
    ''', (result['has_circular_ref'], result['circular_ref_detail'], fp_id))

    # Upsert auto-calculated allergens into finished_product_allergens
    for allergen_name, auto_status in allergen_summary.items():
        try:
            execute('''
                INSERT INTO finished_product_allergens
                    (finished_product_id, allergen_name, notes)
                VALUES (%s, %s, 'auto-calculated')
                ON CONFLICT (finished_product_id, allergen_name) DO NOTHING
            ''', (fp_id, allergen_name))
        except Exception:
            pass
