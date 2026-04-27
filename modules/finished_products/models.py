from core.db import query_one, query_all, execute, execute_returning


def get_all_finished_products(company_id, search=None):
    sql = '''
        SELECT fp.*, e.description AS tool_description, e.tool_number
        FROM finished_products fp
        LEFT JOIN equipment e ON e.id = fp.selected_extrusion_tool_id
        WHERE fp.deleted_at IS NULL AND fp.company_id = %s
    '''
    params = [company_id]
    if search:
        sql += ' AND (fp.name ILIKE %s OR fp.ba_code ILIKE %s)'
        params += [f'%{search}%', f'%{search}%']
    sql += ' ORDER BY fp.name'
    return query_all(sql, params)


def get_deleted_finished_products(company_id):
    return query_all('''
        SELECT * FROM finished_products
        WHERE deleted_at IS NOT NULL AND company_id = %s
        ORDER BY deleted_at DESC
    ''', (company_id,))


def get_finished_product(fp_id):
    return query_one('SELECT * FROM finished_products WHERE id = %s', (fp_id,))


def create_finished_product(data, company_id):
    nw = data.get('net_weight_grams')
    try:
        nw = float(nw) if nw else None
    except (ValueError, TypeError):
        nw = None
    return execute_returning('''
        INSERT INTO finished_products
            (ba_code, name, legal_name, company_id, manufacturer, status, description,
             net_weight_grams, net_weight_unit)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    ''', (
        data.get('ba_code') or None,
        data.get('name'),
        data.get('legal_name') or None,
        company_id,
        data.get('manufacturer') or None,
        data.get('status', 'Draft'),
        data.get('description') or None,
        nw,
        data.get('net_weight_unit', 'g') or 'g',
    ))


def update_finished_product(fp_id, data):
    nw = data.get('net_weight_grams')
    try:
        nw = float(nw) if nw else None
    except (ValueError, TypeError):
        nw = None
    execute('''
        UPDATE finished_products SET
            ba_code=%s, name=%s, legal_name=%s, manufacturer=%s,
            status=%s, description=%s, image_url=%s,
            selected_extrusion_tool_id=%s,
            net_weight_grams=%s, net_weight_unit=%s
        WHERE id = %s
    ''', (
        data.get('ba_code') or None,
        data.get('name'),
        data.get('legal_name') or None,
        data.get('manufacturer') or None,
        data.get('status', 'Draft'),
        data.get('description') or None,
        data.get('image_url') or None,
        int(data['selected_extrusion_tool_id']) if data.get('selected_extrusion_tool_id') else None,
        nw,
        data.get('net_weight_unit', 'g') or 'g',
        fp_id,
    ))


def update_sensory(fp_id, data):
    execute('''
        UPDATE finished_products SET
            d_description=%s, d_colour=%s, d_taste=%s, d_aroma=%s,
            d_texture=%s, d_appearance=%s, d_defects=%s
        WHERE id = %s
    ''', (
        data.get('d_description') or None,
        data.get('d_colour') or None,
        data.get('d_taste') or None,
        data.get('d_aroma') or None,
        data.get('d_texture') or None,
        data.get('d_appearance') or None,
        data.get('d_defects') or None,
        fp_id,
    ))


def update_suitability(fp_id, suitability_json):
    execute('UPDATE finished_products SET suitability_data=%s WHERE id = %s',
            (suitability_json, fp_id))


def soft_delete_finished_product(fp_id, username):
    execute('''
        UPDATE finished_products SET deleted_at=NOW(), deleted_by=%s WHERE id = %s
    ''', (username, fp_id))


def restore_finished_product(fp_id):
    execute('''
        UPDATE finished_products SET deleted_at=NULL, deleted_by=NULL WHERE id = %s
    ''', (fp_id,))


# ---- Recipe ----

def get_recipe_items(fp_id):
    return query_all('''
        SELECT ri.*,
            COALESCE(c.name, fp2.name) AS component_name,
            COALESCE(c.code, fp2.ba_code) AS component_code,
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


def add_recipe_item(fp_id, item_id, item_type, grams_per_unit):
    execute_returning('''
        INSERT INTO finished_product_recipe_items
            (finished_product_id, item_id, item_type, grams_per_unit)
        VALUES (%s, %s, %s, %s) RETURNING id
    ''', (fp_id, item_id, item_type, grams_per_unit))


def delete_recipe_item(item_id):
    execute('DELETE FROM finished_product_recipe_items WHERE id = %s', (item_id,))


# ---- Linked equipment ----

def get_linked_equipment(fp_id):
    return query_all('''
        SELECT e.*, fpe.id AS link_id
        FROM finished_product_equipment fpe
        JOIN equipment e ON e.id = fpe.equipment_id
        WHERE fpe.finished_product_id = %s
        ORDER BY e.tool_number
    ''', (fp_id,))


def link_equipment(fp_id, equipment_id):
    # Avoid duplicate links
    existing = query_one(
        'SELECT id FROM finished_product_equipment WHERE finished_product_id=%s AND equipment_id=%s',
        (fp_id, equipment_id)
    )
    if not existing:
        execute('INSERT INTO finished_product_equipment (finished_product_id, equipment_id) VALUES (%s, %s)',
                (fp_id, equipment_id))


def unlink_equipment(fp_id, equipment_id):
    execute('''
        DELETE FROM finished_product_equipment
        WHERE finished_product_id = %s AND equipment_id = %s
    ''', (fp_id, equipment_id))
