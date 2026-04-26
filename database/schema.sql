-- Specci Manufacturing System — PostgreSQL Schema

-- Company profile (singleton row)
CREATE TABLE IF NOT EXISTS company_profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    name TEXT NOT NULL,
    registration_number TEXT,
    vat_number TEXT,
    address_line1 TEXT,
    address_line2 TEXT,
    city TEXT,
    post_code TEXT,
    country TEXT,
    phone TEXT,
    email TEXT,
    website TEXT,
    fsa_registration TEXT,
    contact_name TEXT,
    contact_position TEXT,
    emergency_contact_name TEXT,
    emergency_contact_position TEXT,
    emergency_email TEXT,
    emergency_phone TEXT,
    factory_address_line1 TEXT,
    factory_address_line2 TEXT,
    factory_city TEXT,
    factory_post_code TEXT,
    factory_country TEXT,
    brc_grade TEXT,
    rspo_certification_number TEXT,
    sedex_membership_number TEXT,
    notes TEXT,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO company_profile (id, name) VALUES (1, 'Your Company Name') ON CONFLICT DO NOTHING;

-- Users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user' CHECK (role IN ('admin', 'user', 'viewer')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Components
CREATE TABLE IF NOT EXISTS components (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE,
    name TEXT NOT NULL,
    component_type TEXT NOT NULL CHECK (
        component_type IN (
            'Mixed Product', 'Finished Product', 'Base Product',
            'Ingredient', 'Sub Ingredient'
        )
    ),
    product_level TEXT NOT NULL DEFAULT 'Component (Manufactured)' CHECK (
        product_level IN (
            'Source Material', 'Raw Material', 'Component (Manufactured)',
            'Component (Purchased)', 'Finished Product (Manufactured)',
            'Finished Product (Purchased)', 'Composite Product', 'Multi-Product Assembly'
        )
    ),
    manufactured_purchased TEXT NOT NULL DEFAULT 'Manufactured' CHECK (
        manufactured_purchased IN ('Manufactured', 'Purchased')
    ),
    description TEXT,
    status TEXT DEFAULT 'Draft',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Suppliers
CREATE TABLE IF NOT EXISTS suppliers (
    id SERIAL PRIMARY KEY,
    supplier_code TEXT NOT NULL UNIQUE,
    supplier_name TEXT NOT NULL,
    address TEXT,
    commercial_contact_name TEXT,
    commercial_contact_email TEXT,
    commercial_contact_landline TEXT,
    commercial_contact_mobile TEXT,
    commercial_contact_role TEXT,
    technical_contact_name TEXT,
    technical_contact_email TEXT,
    technical_contact_landline TEXT,
    technical_contact_mobile TEXT,
    technical_contact_role TEXT,
    emergency_contact_name TEXT,
    emergency_contact_email TEXT,
    emergency_contact_landline TEXT,
    emergency_contact_mobile TEXT,
    emergency_contact_role TEXT,
    accounts_contact_name TEXT,
    accounts_contact_email TEXT,
    accounts_contact_landline TEXT,
    accounts_contact_mobile TEXT,
    accounts_contact_role TEXT,
    supplier_type TEXT,
    last_manufacturer_or_packer_name TEXT,
    last_manufacturer_or_packer_address TEXT,
    approval_status TEXT DEFAULT 'not approved',
    approval_method TEXT,
    approval_scope TEXT,
    approval_date DATE,
    review_date DATE,
    traceability_confirmed BOOLEAN DEFAULT FALSE,
    traceability_system_description TEXT,
    traceability_verification_date DATE,
    clause_reference TEXT,
    notes TEXT,
    last_updated_by TEXT,
    last_updated_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Component <-> Supplier link
CREATE TABLE IF NOT EXISTS component_suppliers (
    component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
    relationship_type TEXT DEFAULT 'Primary',
    lead_time_days INTEGER,
    PRIMARY KEY (component_id, supplier_id)
);

-- Component specifications
CREATE TABLE IF NOT EXISTS component_specifications (
    component_id INTEGER PRIMARY KEY REFERENCES components(id) ON DELETE CASCADE,
    parent_usage TEXT,
    countries_of_manufacture TEXT,
    countries_of_origin TEXT,
    function_primary TEXT,
    function_other TEXT,
    e_numbers TEXT,
    gmo_status TEXT,
    gmo_details TEXT,
    gmo_certificate TEXT,
    palm_oil_status TEXT,
    palm_oil_cert_type TEXT,
    palm_oil_cert_number TEXT,
    special_categories TEXT,
    shelf_life_storage TEXT,
    category_processing_aids TEXT,
    nutrition_energy_kcal FLOAT,
    nutrition_protein FLOAT,
    nutrition_fat FLOAT,
    nutrition_carbohydrate FLOAT,
    nutrition_sugar FLOAT,
    nutrition_fibre FLOAT,
    nutrition_salt FLOAT,
    cocoa_dry_solids FLOAT,
    milk_fat_percent FLOAT,
    heat_treatment_temperature TEXT,
    heat_treatment_time TEXT,
    notes TEXT,
    product_description TEXT,
    product_colour TEXT,
    product_taste TEXT,
    product_aroma TEXT,
    product_texture TEXT,
    product_appearance TEXT,
    product_defects TEXT,
    supplier_recall_withdrawal_process TEXT,
    certification_brc TEXT,
    certification_rspo TEXT,
    certification_utz_fairtrade TEXT,
    certification_halal TEXT,
    certification_kosher TEXT,
    certification_organic TEXT,
    certification_details TEXT,
    commodity_tariff_code TEXT,
    hs_code TEXT,
    current_specification_number TEXT,
    current_specification_issued_date DATE,
    next_spec_review_date DATE,
    meets_uk_retailer_specifications TEXT,
    supermarket_technical_requirements TEXT,
    contains_additives BOOLEAN DEFAULT FALSE,
    contains_colours_flavourings BOOLEAN DEFAULT FALSE,
    scopa_oils_present BOOLEAN DEFAULT FALSE,
    scopa_data JSONB,
    natcol_data JSONB,
    mosh_moah_data JSONB
);

-- Component constituents
CREATE TABLE IF NOT EXISTS component_constituents (
    id SERIAL PRIMARY KEY,
    component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    constituent_component_id INTEGER REFERENCES components(id) ON DELETE SET NULL,
    constituent_name TEXT NOT NULL,
    constituent_ba_code TEXT,
    constituent_level TEXT,
    composition_percent FLOAT,
    declare_on_label BOOLEAN DEFAULT FALSE,
    country_of_origin TEXT,
    country_of_processing TEXT,
    country_of_manufacture TEXT,
    supplier_details TEXT,
    manufacturer_details TEXT,
    notes TEXT,
    e_number TEXT,
    allergen_milk BOOLEAN DEFAULT FALSE,
    allergen_gluten BOOLEAN DEFAULT FALSE,
    allergen_nuts BOOLEAN DEFAULT FALSE,
    allergen_soya BOOLEAN DEFAULT FALSE,
    allergen_eggs BOOLEAN DEFAULT FALSE,
    allergen_fish BOOLEAN DEFAULT FALSE,
    allergen_crustaceans BOOLEAN DEFAULT FALSE,
    allergen_celery BOOLEAN DEFAULT FALSE,
    allergen_mustard BOOLEAN DEFAULT FALSE,
    allergen_sesame BOOLEAN DEFAULT FALSE,
    allergen_sulphites BOOLEAN DEFAULT FALSE,
    allergen_lupin BOOLEAN DEFAULT FALSE,
    allergen_molluscs BOOLEAN DEFAULT FALSE,
    batch_lot_traceable TEXT,
    batch_lot_code TEXT
);

-- Rolled-up allergen status
CREATE TABLE IF NOT EXISTS component_allergens (
    id SERIAL PRIMARY KEY,
    component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    allergen_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Contains', 'May Contain', 'Free From', 'Ingredient Containing')),
    notes TEXT,
    UNIQUE (component_id, allergen_name)
);

-- Analytical parameters
CREATE TABLE IF NOT EXISTS component_analytical_parameters (
    id SERIAL PRIMARY KEY,
    component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    parameter_name TEXT NOT NULL,
    target_value TEXT NOT NULL,
    acceptable_range TEXT NOT NULL,
    typical_value TEXT DEFAULT '',
    method_of_analysis TEXT NOT NULL,
    qc_frequency TEXT NOT NULL,
    UNIQUE (component_id, parameter_name)
);

-- Chemical / physical tests
CREATE TABLE IF NOT EXISTS component_chemical_physical_tests (
    id SERIAL PRIMARY KEY,
    component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    test TEXT,
    target TEXT,
    tolerance TEXT,
    units TEXT,
    method TEXT,
    int_ext TEXT,
    frequency TEXT,
    positive_release TEXT,
    on_c_of_a TEXT
);

-- Microbiological tests
CREATE TABLE IF NOT EXISTS component_micro_tests (
    id SERIAL PRIMARY KEY,
    component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    test_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Required', 'Not Required', 'Completed')),
    notes TEXT,
    test_method TEXT,
    positive_release TEXT,
    UNIQUE (component_id, test_name)
);

-- Contaminants / residues
CREATE TABLE IF NOT EXISTS component_contaminants_residues (
    id SERIAL PRIMARY KEY,
    component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    contaminant_name TEXT NOT NULL,
    maximum_allowable_limit TEXT NOT NULL,
    method_of_analysis TEXT NOT NULL,
    frequency TEXT,
    legislative_reference TEXT
);

-- Storage conditions
CREATE TABLE IF NOT EXISTS component_storage_conditions (
    component_id INTEGER PRIMARY KEY REFERENCES components(id) ON DELETE CASCADE,
    recommended_storage_temp TEXT,
    recommended_storage_temp_unit TEXT DEFAULT '°C',
    max_storage_temp TEXT,
    min_storage_temp TEXT,
    temp_unit TEXT DEFAULT '°C',
    stable_temperature TEXT,
    product_suitable_for_freezing TEXT,
    relative_humidity TEXT,
    humidity_unit TEXT DEFAULT '% RH',
    protection_light_oxygen TEXT,
    protection_light_oxygen_description TEXT,
    avoid_metal_contact TEXT,
    odour_segregation TEXT,
    storage_area_type TEXT,
    shelf_life_from_manufacture_value TEXT,
    shelf_life_from_manufacture_unit TEXT,
    min_shelf_life_on_delivery_value TEXT,
    min_shelf_life_on_delivery_unit TEXT,
    shelf_life_unopened_value TEXT,
    shelf_life_unopened_unit TEXT,
    shelf_life_after_opening_value TEXT,
    shelf_life_after_opening_unit TEXT,
    stock_rotation_requirement TEXT,
    pest_controlled_storage TEXT,
    special_storage_instructions TEXT,
    storage_conditions_combined TEXT
);

-- Packaging levels
CREATE TABLE IF NOT EXISTS component_packaging_levels (
    id SERIAL PRIMARY KEY,
    component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    packaging_level TEXT NOT NULL CHECK (
        packaging_level IN (
            'Primary (Bag/Jar)', 'Secondary (Retail Box)', 'Tertiary (Display Outer/Case)',
            'Shipper/Transit Carton', 'Protective (Interleave/Sheet)', 'Pallet Overwrap', 'Pallet'
        )
    ),
    description_material_type TEXT,
    food_contact TEXT,
    food_contact_compliant TEXT,
    external_dimensions_l TEXT,
    external_dimensions_w TEXT,
    external_dimensions_h TEXT,
    empty_weight_g TEXT,
    filled_weight_g TEXT,
    colour_code TEXT,
    barcode_code TEXT,
    units_per_next_level TEXT,
    recyclable TEXT,
    supplier_origin TEXT,
    other_features TEXT,
    comments_notes TEXT,
    display_order INTEGER DEFAULT 0
);

-- Palletisation
CREATE TABLE IF NOT EXISTS component_palletisation (
    component_id INTEGER PRIMARY KEY REFERENCES components(id) ON DELETE CASCADE,
    units_per_layer TEXT,
    layers_per_pallet TEXT,
    overall_pallet_dimensions_l TEXT,
    overall_pallet_dimensions_w TEXT,
    overall_pallet_dimensions_h TEXT,
    interleave_sheets TEXT,
    shrink_wrap TEXT,
    total_packs_boxes_per_pallet TEXT,
    special_features TEXT
);

-- Coding and lot marking
CREATE TABLE IF NOT EXISTS component_coding_lot_marking (
    component_id INTEGER PRIMARY KEY REFERENCES components(id) ON DELETE CASCADE,
    shelf_life_format_combined TEXT,
    coding_system_combined TEXT,
    code_mark_location_combined TEXT,
    code_mark_format TEXT
);

-- Additives
CREATE TABLE IF NOT EXISTS component_additives (
    id SERIAL PRIMARY KEY,
    component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    legal_name TEXT,
    e_number TEXT,
    function TEXT,
    natural_artificial TEXT,
    level_in_product TEXT
);

-- Palm oil details
CREATE TABLE IF NOT EXISTS component_palm_oil (
    component_id INTEGER PRIMARY KEY REFERENCES components(id) ON DELETE CASCADE,
    contains_palm_oil TEXT,
    rspo_certified TEXT,
    rspo_supply_chain TEXT,
    rspo_cert_number TEXT,
    certified_percentage FLOAT,
    traceability_country TEXT,
    compliance_statement TEXT
);

-- Supplier certificates
CREATE TABLE IF NOT EXISTS certificates_forms (
    id SERIAL PRIMARY KEY,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    reference_or_number TEXT,
    issue_date DATE,
    expiry_date DATE,
    document_upload TEXT,
    send_reminder BOOLEAN DEFAULT FALSE,
    contact_person TEXT,
    contact_email TEXT,
    status TEXT,
    last_updated_by TEXT,
    last_updated_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Ingredients
CREATE TABLE IF NOT EXISTS ingredients (
    id SERIAL PRIMARY KEY,
    ingredient_code TEXT UNIQUE,
    name TEXT NOT NULL,
    specification_code TEXT,
    supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
    risk_assessment_date DATE,
    next_review_date DATE,
    risk_assessment_notes TEXT,
    last_updated_by TEXT,
    last_updated_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Costings
CREATE TABLE IF NOT EXISTS costings (
    id SERIAL PRIMARY KEY,
    component_id INTEGER NOT NULL UNIQUE REFERENCES components(id) ON DELETE CASCADE,
    ingredient_cost FLOAT DEFAULT 0,
    packaging_cost FLOAT DEFAULT 0,
    labor_cost FLOAT DEFAULT 0,
    overhead_cost FLOAT DEFAULT 0,
    margin_percent FLOAT DEFAULT 0,
    currency TEXT DEFAULT 'GBP',
    last_calculated TIMESTAMPTZ DEFAULT NOW()
);

-- Audit trail
CREATE TABLE IF NOT EXISTS audit_trail (
    id SERIAL PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    action TEXT NOT NULL,
    changed_by TEXT,
    changes JSONB,
    notes TEXT,
    module TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    message TEXT,
    type TEXT DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
