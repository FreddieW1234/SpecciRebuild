from core.db import query_one, query_all, execute, execute_returning


def get_all_suppliers(search=None, status=None):
    sql = 'SELECT * FROM suppliers WHERE 1=1'
    params = []
    if search:
        sql += ' AND (supplier_name ILIKE %s OR supplier_code ILIKE %s)'
        params += [f'%{search}%', f'%{search}%']
    if status:
        sql += ' AND approval_status = %s'
        params.append(status)
    sql += ' ORDER BY supplier_name'
    return query_all(sql, params or None)


def get_supplier(supplier_id):
    return query_one('SELECT * FROM suppliers WHERE id = %s', (supplier_id,))


def create_supplier(data):
    return execute_returning("""
        INSERT INTO suppliers (
            supplier_code, supplier_name, address,
            commercial_contact_name, commercial_contact_email, commercial_contact_landline,
            commercial_contact_mobile, commercial_contact_role,
            technical_contact_name, technical_contact_email, technical_contact_landline,
            technical_contact_mobile, technical_contact_role,
            emergency_contact_name, emergency_contact_email, emergency_contact_landline,
            emergency_contact_mobile, emergency_contact_role,
            accounts_contact_name, accounts_contact_email, accounts_contact_landline,
            accounts_contact_mobile, accounts_contact_role,
            supplier_type, last_manufacturer_or_packer_name, last_manufacturer_or_packer_address,
            approval_status, approval_method, approval_scope, approval_date, review_date,
            traceability_confirmed, traceability_system_description, traceability_verification_date,
            clause_reference, notes, last_updated_by
        ) VALUES (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        ) RETURNING id
    """, (
        data.get('supplier_code'), data.get('supplier_name'), data.get('address'),
        data.get('commercial_contact_name'), data.get('commercial_contact_email'),
        data.get('commercial_contact_landline'), data.get('commercial_contact_mobile'),
        data.get('commercial_contact_role'),
        data.get('technical_contact_name'), data.get('technical_contact_email'),
        data.get('technical_contact_landline'), data.get('technical_contact_mobile'),
        data.get('technical_contact_role'),
        data.get('emergency_contact_name'), data.get('emergency_contact_email'),
        data.get('emergency_contact_landline'), data.get('emergency_contact_mobile'),
        data.get('emergency_contact_role'),
        data.get('accounts_contact_name'), data.get('accounts_contact_email'),
        data.get('accounts_contact_landline'), data.get('accounts_contact_mobile'),
        data.get('accounts_contact_role'),
        data.get('supplier_type'),
        data.get('last_manufacturer_or_packer_name'), data.get('last_manufacturer_or_packer_address'),
        data.get('approval_status', 'not approved'), data.get('approval_method'),
        data.get('approval_scope'), data.get('approval_date') or None, data.get('review_date') or None,
        data.get('traceability_confirmed') == 'on',
        data.get('traceability_system_description'), data.get('traceability_verification_date') or None,
        data.get('clause_reference'), data.get('notes'), data.get('last_updated_by'),
    ))


def update_supplier(supplier_id, data):
    execute("""
        UPDATE suppliers SET
            supplier_code=%s, supplier_name=%s, address=%s,
            commercial_contact_name=%s, commercial_contact_email=%s, commercial_contact_landline=%s,
            commercial_contact_mobile=%s, commercial_contact_role=%s,
            technical_contact_name=%s, technical_contact_email=%s, technical_contact_landline=%s,
            technical_contact_mobile=%s, technical_contact_role=%s,
            emergency_contact_name=%s, emergency_contact_email=%s, emergency_contact_landline=%s,
            emergency_contact_mobile=%s, emergency_contact_role=%s,
            accounts_contact_name=%s, accounts_contact_email=%s, accounts_contact_landline=%s,
            accounts_contact_mobile=%s, accounts_contact_role=%s,
            supplier_type=%s, last_manufacturer_or_packer_name=%s, last_manufacturer_or_packer_address=%s,
            approval_status=%s, approval_method=%s, approval_scope=%s,
            approval_date=%s, review_date=%s,
            traceability_confirmed=%s, traceability_system_description=%s,
            traceability_verification_date=%s, clause_reference=%s, notes=%s,
            last_updated_by=%s, last_updated_date=NOW()
        WHERE id = %s
    """, (
        data.get('supplier_code'), data.get('supplier_name'), data.get('address'),
        data.get('commercial_contact_name'), data.get('commercial_contact_email'),
        data.get('commercial_contact_landline'), data.get('commercial_contact_mobile'),
        data.get('commercial_contact_role'),
        data.get('technical_contact_name'), data.get('technical_contact_email'),
        data.get('technical_contact_landline'), data.get('technical_contact_mobile'),
        data.get('technical_contact_role'),
        data.get('emergency_contact_name'), data.get('emergency_contact_email'),
        data.get('emergency_contact_landline'), data.get('emergency_contact_mobile'),
        data.get('emergency_contact_role'),
        data.get('accounts_contact_name'), data.get('accounts_contact_email'),
        data.get('accounts_contact_landline'), data.get('accounts_contact_mobile'),
        data.get('accounts_contact_role'),
        data.get('supplier_type'),
        data.get('last_manufacturer_or_packer_name'), data.get('last_manufacturer_or_packer_address'),
        data.get('approval_status', 'not approved'), data.get('approval_method'),
        data.get('approval_scope'), data.get('approval_date') or None, data.get('review_date') or None,
        data.get('traceability_confirmed') == 'on',
        data.get('traceability_system_description'), data.get('traceability_verification_date') or None,
        data.get('clause_reference'), data.get('notes'), data.get('last_updated_by'),
        supplier_id,
    ))


def delete_supplier(supplier_id):
    execute('DELETE FROM suppliers WHERE id = %s', (supplier_id,))


def get_certificates(supplier_id):
    return query_all('SELECT * FROM certificates_forms WHERE supplier_id = %s ORDER BY created_at DESC', (supplier_id,))


def add_certificate(supplier_id, data):
    execute_returning("""
        INSERT INTO certificates_forms (supplier_id, type, reference_or_number, issue_date, expiry_date,
            send_reminder, contact_person, contact_email, status, last_updated_by)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
    """, (
        supplier_id, data.get('type'), data.get('reference_or_number'),
        data.get('issue_date') or None, data.get('expiry_date') or None,
        data.get('send_reminder') == 'on',
        data.get('contact_person'), data.get('contact_email'),
        data.get('status'), data.get('last_updated_by'),
    ))


def delete_certificate(cert_id):
    execute('DELETE FROM certificates_forms WHERE id = %s', (cert_id,))
