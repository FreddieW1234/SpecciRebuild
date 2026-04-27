ALLERGENS = [
    'Celery', 'Cereals containing gluten', 'Crustaceans', 'Eggs', 'Fish',
    'Lupin', 'Milk', 'Molluscs', 'Mustard', 'Nuts', 'Peanuts',
    'Sesame seeds', 'Soya', 'Sulphur dioxide and sulphites'
]

ALLERGEN_STATUSES = ['Contains', 'May Contain', 'Free From', 'Ingredient Containing']

COMPONENT_TYPES = [
    'Mixed Product', 'Finished Product', 'Base Product', 'Ingredient', 'Sub Ingredient'
]

# Types available when creating/editing components (Finished Product lives in its own module)
COMPONENT_TYPES_FORM = [
    'Mixed Product', 'Base Product', 'Ingredient', 'Sub Ingredient'
]

COMPANY_ASSIGNMENT_OPTIONS = ['Both', 'Michton', 'Bakeart']

PRODUCT_LEVELS = [
    'Source Material', 'Raw Material', 'Component (Manufactured)',
    'Component (Purchased)', 'Finished Product (Manufactured)',
    'Finished Product (Purchased)', 'Composite Product', 'Multi-Product Assembly'
]

GMO_STATUS_OPTIONS = [
    'Non-GMO', 'Contains GMO', 'May Contain GMO', 'GMO-Free Certified', 'Not Assessed'
]

PALM_OIL_STATUS_OPTIONS = [
    'Contains Palm Oil', 'Palm Oil Free', 'May Contain Palm Oil', 'Not Applicable'
]

CERTIFICATION_OPTIONS = ['Yes', 'No', 'In Progress', 'Not Applicable']

COMPONENT_STATUSES = ['Draft', 'Active', 'Under Review', 'Archived']

SUPPLIER_APPROVAL_STATUSES = [
    'not approved', 'approved', 'conditional', 'suspended', 'delisted'
]

CERTIFICATE_TYPES = [
    'BRC/BRCGS', 'ISO 22000', 'FSSC 22000', 'SQF', 'IFS Food',
    'RSPO', 'Fairtrade', 'UTZ', 'Rainforest Alliance', 'Organic',
    'Halal', 'Kosher', 'SEDEX/SMETA', 'Allergen Audit', 'Other'
]

PACKAGING_LEVELS = [
    'Primary (Bag/Jar)', 'Secondary (Retail Box)', 'Tertiary (Display Outer/Case)',
    'Shipper/Transit Carton', 'Protective (Interleave/Sheet)', 'Pallet Overwrap', 'Pallet'
]

COUNTRIES = [
    'United Kingdom', 'Germany', 'France', 'Netherlands', 'Belgium',
    'Spain', 'Italy', 'Poland', 'Czech Republic', 'Hungary',
    'Romania', 'Portugal', 'Sweden', 'Denmark', 'Finland', 'Norway',
    'Switzerland', 'Austria', 'Ireland', 'Greece', 'Turkey',
    'United States', 'Canada', 'Mexico', 'Brazil', 'Argentina',
    'China', 'India', 'Japan', 'South Korea', 'Vietnam', 'Thailand',
    'Indonesia', 'Malaysia', 'Philippines', 'Australia', 'New Zealand',
    'South Africa', 'Nigeria', 'Kenya', 'Ghana', 'Egypt', 'Morocco',
    'Colombia', 'Peru', 'Ecuador', 'Ivory Coast', 'Cameroon',
    'Dominican Republic', 'Sri Lanka', 'Pakistan', 'Bangladesh',
]

NUTRITION_FIELDS = [
    {'key': 'nutrition_energy_kcal', 'label': 'Energy (kcal)', 'unit': 'kcal'},
    {'key': 'nutrition_protein', 'label': 'Protein', 'unit': 'g'},
    {'key': 'nutrition_fat', 'label': 'Fat', 'unit': 'g'},
    {'key': 'nutrition_carbohydrate', 'label': 'Carbohydrate', 'unit': 'g'},
    {'key': 'nutrition_sugar', 'label': 'of which sugars', 'unit': 'g'},
    {'key': 'nutrition_fibre', 'label': 'Fibre', 'unit': 'g'},
    {'key': 'nutrition_salt', 'label': 'Salt', 'unit': 'g'},
]

MICRO_TEST_NAMES = [
    'Total Viable Count (TVC)',
    'Yeast & Mould',
    'Enterobacteriaceae',
    'E. coli',
    'Salmonella',
    'Listeria monocytogenes',
    'Staphylococcus aureus',
    'Coliforms',
    'Bacillus cereus',
    'Campylobacter',
]
