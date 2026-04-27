from flask import Flask, g, session, redirect, url_for, request, flash
from config import SECRET_KEY, DEBUG


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DEBUG'] = DEBUG

    # Jinja2 globals and filters
    app.jinja_env.globals['enumerate'] = enumerate
    app.jinja_env.globals['zip'] = zip

    # ---- Blueprints ----

    # Core modules
    from modules.components import bp as components_bp
    from modules.suppliers import bp as suppliers_bp
    from modules.specifications import bp as specifications_bp

    # New full modules
    from modules.finished_products import bp as finished_products_bp
    from modules.product_templates import bp as product_templates_bp
    from modules.packaging import bp as packaging_bp          # replaces stub
    from modules.equipment import bp as equipment_bp
    from modules.users import bp as users_bp

    # Stub modules
    from modules.pricing import bp as pricing_bp
    from modules.quality import bp as quality_bp
    from modules.production import bp as production_bp
    from modules.inventory import bp as inventory_bp
    from modules.traceability import bp as traceability_bp
    from modules.supply_chain import bp as supply_chain_bp
    from modules.sales import bp as sales_bp
    from modules.finance import bp as finance_bp
    from modules.crm import bp as crm_bp
    from modules.rnd import bp as rnd_bp
    from modules.maintenance import bp as maintenance_bp
    from modules.hr import bp as hr_bp
    from modules.shopfloor import bp as shopfloor_bp
    from modules.documents import bp as documents_bp
    from modules.compliance import bp as compliance_bp
    from modules.marketing import bp as marketing_bp
    from modules.website import bp as website_bp
    from modules.reporting import bp as reporting_bp
    from modules.help_center import bp as help_center_bp

    # Auth & dashboard
    from core.auth import bp as auth_bp
    from modules.dashboard import bp as dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(finished_products_bp)
    app.register_blueprint(components_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(specifications_bp)
    app.register_blueprint(product_templates_bp)
    app.register_blueprint(packaging_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(pricing_bp)
    app.register_blueprint(quality_bp)
    app.register_blueprint(production_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(traceability_bp)
    app.register_blueprint(supply_chain_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(crm_bp)
    app.register_blueprint(rnd_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(hr_bp)
    app.register_blueprint(shopfloor_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(compliance_bp)
    app.register_blueprint(marketing_bp)
    app.register_blueprint(website_bp)
    app.register_blueprint(reporting_bp)
    app.register_blueprint(help_center_bp)

    # ---- Company switcher route ----
    @app.route('/set-company/<int:company_id>', methods=['POST'])
    def set_company(company_id):
        session['active_company_id'] = company_id
        return redirect(request.referrer or url_for('dashboard.index'))

    # ---- Before-request hooks ----
    @app.before_request
    def load_user():
        g.current_user = None
        uid = session.get('user_id')
        if uid:
            from core.auth import get_user_by_id
            g.current_user = get_user_by_id(uid)

    @app.before_request
    def require_login():
        public_prefixes = ['/login', '/static', '/setup']
        if any(request.path.startswith(p) for p in public_prefixes):
            return
        if not g.get('current_user'):
            return redirect(url_for('auth.login'))

    # ---- Context processor — injects active_company + all_companies into every template ----
    @app.context_processor
    def inject_company():
        from core.auth import get_active_company, get_all_companies
        try:
            active = get_active_company()
            companies = get_all_companies()
        except Exception:
            active = {'id': 1, 'name': 'Specci'}
            companies = []
        return dict(active_company=active, all_companies=companies)

    # ---- Schema migrations ----
    from core.db import ensure_schema
    try:
        ensure_schema()
    except Exception:
        pass

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=DEBUG)
