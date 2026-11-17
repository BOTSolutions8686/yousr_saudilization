"""Run only on the explicitly approved disposable site after its native setup.

Use bench execute with a trusted operator; this file is NOT an app hook or API.
It creates fictional data only after the exact-site/config guards. No cleanup or
provider operation is implemented here. External HTTP and mail calls are denied.
"""
from unittest.mock import patch

import frappe
from yousr_saudilization import demo_setup as demo


def run():
    site = str(frappe.local.site)
    assert site.startswith('demo-setup-qa-'), 'Refuse non-QA site'
    assert frappe.conf.get('yousr_demo_qa') is True, 'Explicit QA switch required'
    assert frappe.session.user == 'Administrator', 'QA administrator only'
    assert frappe.is_setup_complete(), 'Finish native QA setup first'
    companies = frappe.get_all('Company', pluck='name')
    assert len(companies) == 1 and demo.COMPANY not in companies
    real = companies[0]
    before = (demo._defaults(), frappe.get_doc('Company', real).as_json(),
              frappe.db.count('Sales Invoice'), frappe.db.count('GL Entry'), frappe.db.count('Stock Ledger Entry'))
    state = demo._state()
    assert not state.status and not state.records
    state.real_company = real
    state.records = '[]'
    state.status = 'Queued'
    demo._save(state)
    frappe.db.commit()

    # An injected failure must roll back company, native child setup and masters.
    original = demo._insert
    calls = 0
    def fail_after_company(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 3:
            raise RuntimeError('Deliberate QA failure')
        return original(*args, **kwargs)
    with patch.object(demo, '_insert', fail_after_company), patch('requests.sessions.Session.request', side_effect=AssertionError('External HTTP forbidden')), patch.object(frappe, 'sendmail', side_effect=AssertionError('Mail forbidden')):
        demo.create_demo()
    assert demo._state().status == 'Failed'
    assert not frappe.db.exists('Company', demo.COMPANY)
    assert demo._manifest(demo._state()) == []
    assert before[0] == demo._defaults()

    # Retry through the same implementation and prove idempotence.
    with patch('requests.sessions.Session.request', side_effect=AssertionError('External HTTP forbidden')), patch.object(frappe, 'sendmail', side_effect=AssertionError('Mail forbidden')):
        demo.create_demo()
        assert demo._state().status == 'Ready', demo._state().error_code
        manifest = demo._manifest(demo._state())
        assert len(manifest) == 13, manifest
        demo.create_demo()
        assert demo._manifest(demo._state()) == manifest
        after = (demo._defaults(), frappe.get_doc('Company', real).as_json(),
                 frappe.db.count('Sales Invoice'), frappe.db.count('GL Entry'), frappe.db.count('Stock Ledger Entry'))
        assert before == after, 'Real defaults/company or financial records changed'
        for row in manifest:
            doc = frappe.get_doc(row['doctype'], row['name'])
            if doc.meta.is_submittable:
                assert doc.docstatus == 0
        assert not frappe.db.get_value('Company', demo.COMPANY, 'tax_id')
        frappe.db.commit()  # Retain approved fictional seed for the following UI checks.
        quotation = next(r for r in manifest if r['doctype'] == 'Quotation')
        doc = frappe.get_doc('Quotation', quotation['name'])
        try:
            doc.submit()
        except frappe.ValidationError:
            pass
        else:
            raise AssertionError('Practice submission was not blocked')
        doc = frappe.get_doc('Quotation', quotation['name'])
        doc.company = real
        try:
            doc.save()
        except frappe.ValidationError:
            pass
        else:
            raise AssertionError('Demo records entered real company')
    frappe.db.rollback()  # Do not persist validation-test edits; seeded data is QA-only.
    return {'site':site, 'default_company_unchanged':True, 'real_company_unchanged':True,
            'practice_records':len(manifest), 'idempotent':True, 'partial_failure_rolled_back':True,
            'mixed_company_save_blocked':True, 'practice_submission_blocked':True,
            'invoices_created':0,'gl_entries_created':0,'stock_entries_created':0,
            'zatca_mode':'simulated_examples_only','live_http_and_mail':'denied'}
