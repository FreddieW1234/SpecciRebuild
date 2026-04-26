from flask import render_template, request, redirect, url_for, flash, g
from modules.suppliers import bp
from modules.suppliers.models import (
    get_all_suppliers, get_supplier, create_supplier, update_supplier, delete_supplier,
    get_certificates, add_certificate, delete_certificate,
)
from core.decorators import login_required
from core.reference_data import SUPPLIER_APPROVAL_STATUSES, CERTIFICATE_TYPES


@bp.route('/')
@login_required
def index():
    search = request.args.get('q', '').strip()
    status = request.args.get('status', '').strip()
    suppliers = get_all_suppliers(search=search or None, status=status or None)
    return render_template('suppliers/index.html', suppliers=suppliers, search=search,
                           status_filter=status, approval_statuses=SUPPLIER_APPROVAL_STATUSES)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        data = request.form.to_dict()
        data['last_updated_by'] = g.current_user['username']
        if not data.get('supplier_name'):
            flash('Supplier name is required.', 'error')
            return render_template('suppliers/form.html', supplier=data, is_new=True,
                                   approval_statuses=SUPPLIER_APPROVAL_STATUSES)
        sid = create_supplier(data)
        flash('Supplier created.', 'success')
        return redirect(url_for('suppliers.detail', id=sid))
    return render_template('suppliers/form.html', supplier={}, is_new=True,
                           approval_statuses=SUPPLIER_APPROVAL_STATUSES)


@bp.route('/<int:id>')
@login_required
def detail(id):
    supplier = get_supplier(id)
    if not supplier:
        flash('Supplier not found.', 'error')
        return redirect(url_for('suppliers.index'))
    certs = get_certificates(id)
    return render_template('suppliers/detail.html', supplier=supplier, certs=certs,
                           cert_types=CERTIFICATE_TYPES)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    supplier = get_supplier(id)
    if not supplier:
        flash('Supplier not found.', 'error')
        return redirect(url_for('suppliers.index'))
    if request.method == 'POST':
        data = request.form.to_dict()
        data['last_updated_by'] = g.current_user['username']
        if not data.get('supplier_name'):
            flash('Supplier name is required.', 'error')
            return render_template('suppliers/form.html', supplier=data, is_new=False,
                                   approval_statuses=SUPPLIER_APPROVAL_STATUSES)
        update_supplier(id, data)
        flash('Supplier updated.', 'success')
        return redirect(url_for('suppliers.detail', id=id))
    return render_template('suppliers/form.html', supplier=supplier, is_new=False,
                           approval_statuses=SUPPLIER_APPROVAL_STATUSES)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    delete_supplier(id)
    flash('Supplier deleted.', 'success')
    return redirect(url_for('suppliers.index'))


@bp.route('/<int:id>/certificates', methods=['POST'])
@login_required
def add_cert(id):
    data = request.form.to_dict()
    data['last_updated_by'] = g.current_user['username']
    add_certificate(id, data)
    flash('Certificate added.', 'success')
    return redirect(url_for('suppliers.detail', id=id) + '#certificates')


@bp.route('/<int:id>/certificates/<int:cid>/delete', methods=['POST'])
@login_required
def delete_cert(id, cid):
    delete_certificate(cid)
    flash('Certificate removed.', 'success')
    return redirect(url_for('suppliers.detail', id=id) + '#certificates')
