from core.db import query_one, query_all, execute, execute_returning


# ---- Components ----

def get_all_components(search=None, type_filter=None, status_filter=None, company_short=None):
    sql = "SELECT * FROM components WHERE component_type != 'Finished Product'"
    params = []
    if company_short:
        sql += " AND (company_assignment = 'Both' OR company_assignment = %s)"
        params.append(company_short)
    if search:
        sql += ' AND (name ILIKE %s OR code ILIKE %s)'
        params += [f'%{search}%', f'%{search}%']
    if type_filter:
        sql += ' AND component_type = %s'
        params.append(type_filter)
    if status_filter:
        sql += ' AND status = %s'
        params.append(status_filter)
    sql += ' ORDER BY name'
    return query_all(sql, params or None)


def get_component(component_id):
    return query_one('SELECT * FROM components WHERE id = %s', (component_id,))


def create_component(data):
    return execute_returning("""
        INSERT INTO components
            (code, name, component_type, product_level, manufactured_purchased,
             description, status, company_assignment)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
    """, (
        data.get('code') or None,
        data.get('name'),
        data.get('component_type'),
        data.get('product_level', 'Component (Manufactured)'),
        data.get('manufactured_purchased', 'Manufactured'),
        data.get('description'),
        data.get('status', 'Draft'),
        data.get('company_assignment', 'Both'),
    ))


def update_component(component_id, data):
    execute("""
        UPDATE components SET code=%s, name=%s, component_type=%s, product_level=%s,
            manufactured_purchased=%s, description=%s, status=%s,
            company_assignment=%s, updated_at=NOW()
        WHERE id = %s
    """, (
        data.get('code') or None,
        data.get('name'),
        data.get('component_type'),
        data.get('product_level', 'Component (Manufactured)'),
        data.get('manufactured_purchased', 'Manufactured'),
        data.get('description'),
        data.get('status', 'Draft'),
        data.get('company_assignment', 'Both'),
        component_id,
    ))


def delete_component(component_id):
    execute('DELETE FROM components WHERE id = %s', (component_id,))


# ---- Specifications ----

def get_spec(component_id):
    return query_one('SELECT * FROM component_specifications WHERE component_id = %s', (component_id,))


def upsert_spec(component_id, data):
    existing = get_spec(component_id)
    fields = [
        'parent_usage', 'countries_of_manufacture', 'countries_of_origin',
        'function_primary', 'function_other', 'e_numbers',
        'gmo_status', 'gmo_details', 'gmo_certificate',
        'palm_oil_status', 'palm_oil_cert_type', 'palm_oil_cert_number',
        'special_categories', 'shelf_life_storage', 'category_processing_aids',
        'nutrition_energy_kcal', 'nutrition_protein', 'nutrition_fat',
        'nutrition_carbohydrate', 'nutrition_sugar', 'nutrition_fibre', 'nutrition_salt',
        'cocoa_dry_solids', 'milk_fat_percent',
        'heat_treatment_temperature', 'heat_treatment_time', 'notes',
        'product_description', 'product_colour', 'product_taste', 'product_aroma',
        'product_texture', 'product_appearance', 'product_defects',
        'supplier_recall_withdrawal_process',
        'certification_brc', 'certification_rspo', 'certification_utz_fairtrade',
        'certification_halal', 'certification_kosher', 'certification_organic',
        'certification_details', 'commodity_tariff_code', 'hs_code',
        'current_specification_number', 'current_specification_issued_date',
        'next_spec_review_date', 'meets_uk_retailer_specifications',
        'supermarket_technical_requirements',
    ]
    bool_fields = ['contains_additives', 'contains_colours_flavourings', 'scopa_oils_present']
    float_fields = ['nutrition_energy_kcal', 'nutrition_protein', 'nutrition_fat',
                    'nutrition_carbohydrate', 'nutrition_sugar', 'nutrition_fibre', 'nutrition_salt',
                    'cocoa_dry_solids', 'milk_fat_percent']
    date_fields = ['current_specification_issued_date', 'next_spec_review_date']

    def val(k):
        if k in bool_fields:
            return data.get(k) == 'on'
        v = data.get(k)
        if k in float_fields:
            try:
                return float(v) if v else None
            except (TypeError, ValueError):
                return None
        if k in date_fields:
            return v or None
        return v or None

    all_fields = fields + bool_fields
    values = [val(k) for k in all_fields]

    if existing:
        set_clause = ', '.join(f'{k}=%s' for k in all_fields)
        execute(f'UPDATE component_specifications SET {set_clause} WHERE component_id=%s',
                values + [component_id])
    else:
        cols = ', '.join(all_fields)
        placeholders = ', '.join(['%s'] * len(all_fields))
        execute(f'INSERT INTO component_specifications (component_id, {cols}) VALUES (%s, {placeholders})',
                [component_id] + values)


# ---- Constituents ----

def get_constituents(component_id):
    return query_all('SELECT * FROM component_constituents WHERE component_id = %s ORDER BY id', (component_id,))


def upsert_constituents(component_id, rows):
    execute('DELETE FROM component_constituents WHERE component_id = %s', (component_id,))
    for row in rows:
        if not row.get('constituent_name'):
            continue
        execute("""
            INSERT INTO component_constituents (
                component_id, constituent_name, constituent_ba_code, constituent_level,
                composition_percent, declare_on_label, country_of_origin,
                country_of_processing, country_of_manufacture, supplier_details,
                manufacturer_details, notes, e_number,
                allergen_milk, allergen_gluten, allergen_nuts, allergen_soya,
                allergen_eggs, allergen_fish, allergen_crustaceans, allergen_celery,
                allergen_mustard, allergen_sesame, allergen_sulphites, allergen_lupin,
                allergen_molluscs, batch_lot_traceable, batch_lot_code
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            component_id,
            row.get('constituent_name'),
            row.get('constituent_ba_code'),
            row.get('constituent_level'),
            float(row['composition_percent']) if row.get('composition_percent') else None,
            row.get('declare_on_label') == 'on',
            row.get('country_of_origin'),
            row.get('country_of_processing'),
            row.get('country_of_manufacture'),
            row.get('supplier_details'),
            row.get('manufacturer_details'),
            row.get('notes'),
            row.get('e_number'),
            row.get('allergen_milk') == 'on',
            row.get('allergen_gluten') == 'on',
            row.get('allergen_nuts') == 'on',
            row.get('allergen_soya') == 'on',
            row.get('allergen_eggs') == 'on',
            row.get('allergen_fish') == 'on',
            row.get('allergen_crustaceans') == 'on',
            row.get('allergen_celery') == 'on',
            row.get('allergen_mustard') == 'on',
            row.get('allergen_sesame') == 'on',
            row.get('allergen_sulphites') == 'on',
            row.get('allergen_lupin') == 'on',
            row.get('allergen_molluscs') == 'on',
            row.get('batch_lot_traceable'),
            row.get('batch_lot_code'),
        ))


# ---- Allergens ----

def get_allergens(component_id):
    return query_all('SELECT * FROM component_allergens WHERE component_id = %s ORDER BY allergen_name', (component_id,))


def upsert_allergens(component_id, allergen_data):
    for allergen_name, status in allergen_data.items():
        if not status:
            continue
        notes = allergen_data.get(f'{allergen_name}__notes', '')
        existing = query_one('SELECT id FROM component_allergens WHERE component_id=%s AND allergen_name=%s',
                             (component_id, allergen_name))
        if existing:
            execute('UPDATE component_allergens SET status=%s, notes=%s WHERE component_id=%s AND allergen_name=%s',
                    (status, notes, component_id, allergen_name))
        else:
            execute('INSERT INTO component_allergens (component_id, allergen_name, status, notes) VALUES (%s,%s,%s,%s)',
                    (component_id, allergen_name, status, notes))


# ---- Storage ----

def get_storage(component_id):
    return query_one('SELECT * FROM component_storage_conditions WHERE component_id = %s', (component_id,))


def upsert_storage(component_id, data):
    existing = get_storage(component_id)
    fields = [
        'recommended_storage_temp', 'recommended_storage_temp_unit',
        'max_storage_temp', 'min_storage_temp', 'temp_unit', 'stable_temperature',
        'product_suitable_for_freezing', 'relative_humidity', 'humidity_unit',
        'protection_light_oxygen', 'protection_light_oxygen_description',
        'avoid_metal_contact', 'odour_segregation', 'storage_area_type',
        'shelf_life_from_manufacture_value', 'shelf_life_from_manufacture_unit',
        'min_shelf_life_on_delivery_value', 'min_shelf_life_on_delivery_unit',
        'shelf_life_unopened_value', 'shelf_life_unopened_unit',
        'shelf_life_after_opening_value', 'shelf_life_after_opening_unit',
        'stock_rotation_requirement', 'pest_controlled_storage',
        'special_storage_instructions', 'storage_conditions_combined',
    ]
    values = [data.get(f) or None for f in fields]
    if existing:
        set_clause = ', '.join(f'{f}=%s' for f in fields)
        execute(f'UPDATE component_storage_conditions SET {set_clause} WHERE component_id=%s', values + [component_id])
    else:
        cols = ', '.join(fields)
        placeholders = ', '.join(['%s'] * len(fields))
        execute(f'INSERT INTO component_storage_conditions (component_id, {cols}) VALUES (%s, {placeholders})',
                [component_id] + values)


# ---- Packaging ----

def get_packaging(component_id):
    return query_all('SELECT * FROM component_packaging_levels WHERE component_id = %s ORDER BY display_order', (component_id,))


def upsert_packaging(component_id, rows):
    execute('DELETE FROM component_packaging_levels WHERE component_id = %s', (component_id,))
    for i, row in enumerate(rows):
        if not row.get('packaging_level'):
            continue
        execute("""
            INSERT INTO component_packaging_levels (
                component_id, packaging_level, description_material_type, food_contact,
                food_contact_compliant, external_dimensions_l, external_dimensions_w, external_dimensions_h,
                empty_weight_g, filled_weight_g, colour_code, barcode_code,
                units_per_next_level, recyclable, supplier_origin, other_features,
                comments_notes, display_order
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            component_id, row.get('packaging_level'), row.get('description_material_type'),
            row.get('food_contact'), row.get('food_contact_compliant'),
            row.get('external_dimensions_l'), row.get('external_dimensions_w'), row.get('external_dimensions_h'),
            row.get('empty_weight_g'), row.get('filled_weight_g'),
            row.get('colour_code'), row.get('barcode_code'),
            row.get('units_per_next_level'), row.get('recyclable'),
            row.get('supplier_origin'), row.get('other_features'),
            row.get('comments_notes'), i,
        ))


# ---- Analytical Parameters ----

def get_analytical(component_id):
    return query_all('SELECT * FROM component_analytical_parameters WHERE component_id = %s ORDER BY id', (component_id,))


def upsert_analytical(component_id, rows):
    execute('DELETE FROM component_analytical_parameters WHERE component_id = %s', (component_id,))
    for row in rows:
        if not row.get('parameter_name'):
            continue
        execute("""
            INSERT INTO component_analytical_parameters
                (component_id, parameter_name, target_value, acceptable_range, typical_value, method_of_analysis, qc_frequency)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            component_id, row.get('parameter_name'), row.get('target_value', ''),
            row.get('acceptable_range', ''), row.get('typical_value', ''),
            row.get('method_of_analysis', ''), row.get('qc_frequency', ''),
        ))


# ---- Micro Tests ----

def get_micro(component_id):
    return query_all('SELECT * FROM component_micro_tests WHERE component_id = %s ORDER BY test_name', (component_id,))


def upsert_micro(component_id, rows):
    execute('DELETE FROM component_micro_tests WHERE component_id = %s', (component_id,))
    for row in rows:
        if not row.get('test_name'):
            continue
        execute("""
            INSERT INTO component_micro_tests (component_id, test_name, status, notes, test_method, positive_release)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            component_id, row.get('test_name'),
            row.get('status', 'Required'),
            row.get('notes'), row.get('test_method'), row.get('positive_release'),
        ))


# ---- Additives ----

def get_additives(component_id):
    return query_all('SELECT * FROM component_additives WHERE component_id = %s ORDER BY id', (component_id,))


def upsert_additives(component_id, rows):
    execute('DELETE FROM component_additives WHERE component_id = %s', (component_id,))
    for row in rows:
        if not row.get('legal_name') and not row.get('e_number'):
            continue
        execute("""
            INSERT INTO component_additives (component_id, legal_name, e_number, function, natural_artificial, level_in_product)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            component_id, row.get('legal_name'), row.get('e_number'),
            row.get('function'), row.get('natural_artificial'), row.get('level_in_product'),
        ))


# ---- Palm Oil ----

def get_palm(component_id):
    return query_one('SELECT * FROM component_palm_oil WHERE component_id = %s', (component_id,))


def upsert_palm(component_id, data):
    existing = get_palm(component_id)
    fields = ['contains_palm_oil', 'rspo_certified', 'rspo_supply_chain', 'rspo_cert_number',
              'certified_percentage', 'traceability_country', 'compliance_statement']
    def val(k):
        v = data.get(k)
        if k == 'certified_percentage':
            try:
                return float(v) if v else None
            except (TypeError, ValueError):
                return None
        return v or None
    values = [val(k) for k in fields]
    if existing:
        set_clause = ', '.join(f'{k}=%s' for k in fields)
        execute(f'UPDATE component_palm_oil SET {set_clause} WHERE component_id=%s', values + [component_id])
    else:
        cols = ', '.join(fields)
        placeholders = ', '.join(['%s'] * len(fields))
        execute(f'INSERT INTO component_palm_oil (component_id, {cols}) VALUES (%s, {placeholders})',
                [component_id] + values)
