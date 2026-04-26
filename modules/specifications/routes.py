from flask import render_template, request, redirect, url_for, flash, make_response
from modules.specifications import bp
from modules.components.models import (
    get_component, get_spec, upsert_spec,
    get_constituents, get_allergens, get_storage,
    get_analytical, get_micro, get_additives, get_palm,
)
from core.decorators import login_required
from core.db import query_all, query_one
from core.reference_data import (
    ALLERGENS, ALLERGEN_STATUSES, GMO_STATUS_OPTIONS,
    PALM_OIL_STATUS_OPTIONS, CERTIFICATION_OPTIONS, NUTRITION_FIELDS,
)


def _load_spec_context(component_id):
    component = get_component(component_id)
    if not component:
        return None
    spec = get_spec(component_id) or {}
    constituents = get_constituents(component_id)
    allergens_list = get_allergens(component_id)
    allergen_map = {a['allergen_name']: a for a in allergens_list}
    storage = get_storage(component_id) or {}
    analytical = get_analytical(component_id)
    micro = get_micro(component_id)
    additives = get_additives(component_id)
    palm = get_palm(component_id) or {}
    company = query_one('SELECT * FROM company_profile WHERE id = 1')
    # Get linked suppliers
    suppliers = query_all("""
        SELECT s.supplier_name, s.supplier_code, cs.relationship_type
        FROM component_suppliers cs
        JOIN suppliers s ON s.id = cs.supplier_id
        WHERE cs.component_id = %s
        ORDER BY cs.relationship_type, s.supplier_name
    """, (component_id,))
    return dict(
        component=component, spec=spec, constituents=constituents,
        allergens=ALLERGENS, allergen_map=allergen_map,
        storage=storage, analytical=analytical, micro=micro,
        additives=additives, palm=palm, company=company or {},
        suppliers=suppliers, nutrition_fields=NUTRITION_FIELDS,
    )


@bp.route('/')
@login_required
def index():
    components = query_all("""
        SELECT c.id, c.code, c.name, c.component_type, c.status,
               cs.current_specification_number, cs.next_spec_review_date
        FROM components c
        LEFT JOIN component_specifications cs ON cs.component_id = c.id
        ORDER BY c.name
    """)
    return render_template('specifications/index.html', components=components)


@bp.route('/<int:component_id>/preview')
@login_required
def preview(component_id):
    ctx = _load_spec_context(component_id)
    if not ctx:
        flash('Component not found.', 'error')
        return redirect(url_for('specifications.index'))
    return render_template('specifications/spec_sheet.html', **ctx, is_pdf=False)


@bp.route('/<int:component_id>/pdf')
@login_required
def pdf(component_id):
    ctx = _load_spec_context(component_id)
    if not ctx:
        flash('Component not found.', 'error')
        return redirect(url_for('specifications.index'))
    html = render_template('specifications/spec_sheet.html', **ctx, is_pdf=True)
    try:
        from weasyprint import HTML
        pdf_bytes = HTML(string=html, base_url=request.host_url).write_pdf()
        name = ctx['component'].get('code') or ctx['component']['name']
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{name}_spec.pdf"'
        return response
    except Exception as e:
        flash(f'PDF generation failed: {e}', 'error')
        return redirect(url_for('specifications.preview', component_id=component_id))


@bp.route('/<int:component_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(component_id):
    component = get_component(component_id)
    if not component:
        flash('Component not found.', 'error')
        return redirect(url_for('specifications.index'))
    if request.method == 'POST':
        upsert_spec(component_id, request.form.to_dict())
        flash('Specification saved.', 'success')
        return redirect(url_for('specifications.preview', component_id=component_id))
    spec = get_spec(component_id) or {}
    return render_template('specifications/edit.html', component=component, spec=spec,
                           gmo_options=GMO_STATUS_OPTIONS, palm_options=PALM_OIL_STATUS_OPTIONS,
                           cert_options=CERTIFICATION_OPTIONS, nutrition_fields=NUTRITION_FIELDS)
