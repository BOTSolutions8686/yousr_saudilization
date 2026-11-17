"""No Frappe/server needed: strict boundaries and safe native-setup extension contracts."""
import importlib
import sys
import types
import unittest
from unittest.mock import Mock


class Document:
    def __init__(self, doctype, **values):
        self.doctype = doctype
        self.name = values.pop('name', None)
        self.values = values
        self.meta = types.SimpleNamespace(fields=[], get_link_fields=lambda: values.get('_links', []))
    def get(self, key):
        return self.name if key == 'name' else self.values.get(key)
    def get_all_children(self):
        return self.values.get('_children', [])


def link(field, target):
    return types.SimpleNamespace(fieldname=field, options=target, fieldtype='Link')


class DemoSetupTest(unittest.TestCase):
    def setUp(self):
        def deny(message, *args):
            raise ValueError(message)
        self.frappe = types.SimpleNamespace(
            conf={}, session=types.SimpleNamespace(user='Administrator'),
            whitelist=lambda **kw: lambda f:f, _=lambda x:x,
            throw=deny, PermissionError=PermissionError, only_for=Mock(),
            db=types.SimpleNamespace(exists=Mock(return_value=True), after_commit=types.SimpleNamespace(add=Mock()), commit=Mock()),
            enqueue=Mock(), log_error=Mock(), get_single=Mock(),
        )
        sys.modules['frappe'] = self.frappe
        sys.modules.pop('yousr_saudilization.demo_setup', None)
        self.m = importlib.import_module('yousr_saudilization.demo_setup')

    def test_opt_out_and_disabled_feature_never_enqueue_or_read_customer_data(self):
        for value in [None, False, 0, '0', 'false']:
            self.m.request_after_setup({'yousr_load_demo':value})
        self.frappe.get_single.assert_not_called()
        self.frappe.enqueue.assert_not_called()
        self.frappe.conf['yousr_demo_enabled'] = False
        self.m.request_after_setup({'yousr_load_demo':1})
        self.frappe.enqueue.assert_not_called()

    def test_opt_in_queues_only_after_commit_and_duplicate_setup_does_not_reseed(self):
        state=types.SimpleNamespace(status='',records='',save=Mock())
        self.frappe.get_single.return_value=state
        self.frappe.db.exists.side_effect=lambda doctype,name:name=='Real Company'
        self.m.request_after_setup({'yousr_load_demo':1,'company_name':'Real Company'})
        self.assertEqual(state.status,'Queued')
        self.assertEqual(state.real_company,'Real Company')
        self.frappe.enqueue.assert_not_called()
        self.frappe.db.after_commit.add.assert_called_once_with(self.m._enqueue_safely)
        self.m._enqueue_safely()
        self.frappe.enqueue.assert_called_once()
        self.m.request_after_setup({'yousr_load_demo':1,'company_name':'Real Company'})
        self.frappe.db.after_commit.add.assert_called_once()

    def test_native_setup_does_not_fail_when_optional_queueing_fails(self):
        self.frappe.get_single.side_effect = RuntimeError('queue unavailable')
        self.m.request_after_setup({'yousr_load_demo':1,'company_name':'Real Company'})
        self.frappe.log_error.assert_called_once()

    def test_queue_failure_after_commit_is_contained_and_retryable(self):
        state=types.SimpleNamespace(status='Queued',records='[]',save=Mock())
        self.frappe.get_single.return_value=state
        self.frappe.enqueue.side_effect=RuntimeError('Redis unavailable')
        self.m._enqueue_safely()
        self.assertEqual(state.status,'Failed')
        self.assertEqual(state.error_code,'practice_queue_unavailable')
        self.frappe.db.commit.assert_called_once()

    def test_guest_cannot_access_status_or_retry(self):
        self.frappe.session.user = 'Guest'
        with self.assertRaises(ValueError): self.m.status()
        with self.assertRaises(ValueError): self.m.retry()
        self.frappe.get_single.assert_not_called()

    def test_real_records_are_not_modified_or_subject_to_demo_submission_block(self):
        d=Document('Sales Invoice',name='REAL-001',company='Real Company',customer='Real Customer',_links=[link('customer','Customer')])
        self.m.guard_document(d)
        self.m.block_submission(d)
        self.assertEqual(d.get('company'),'Real Company')
        self.frappe.db.exists.assert_not_called()

    def test_demo_customer_and_item_cannot_enter_real_company_including_child_rows(self):
        for field, target in [('customer','Customer'),('supplier','Supplier')]:
            d=Document('Sales Invoice',company='Real Company',**{field:'YOUSR-DEMO-Sample', '_links':[link(field,target)]})
            with self.assertRaises(ValueError):self.m.guard_document(d)
        child=Document('Sales Invoice Item',item_code='YOUSR-DEMO-DESK',_links=[link('item_code','Item')])
        with self.assertRaises(ValueError):self.m.guard_document(Document('Sales Invoice',company='Real Company',_children=[child]))

    def test_real_customer_or_item_cannot_enter_demo_company(self):
        for target in ['Customer','Item','Price List']:
            d=Document('Quotation',company=self.m.COMPANY,reference='Real master',_links=[link('reference',target)])
            with self.assertRaises(ValueError):self.m.guard_document(d)

    def test_demo_drafts_are_allowed_but_never_submitted(self):
        d=Document('Sales Invoice',company=self.m.COMPANY,customer='YOUSR-DEMO-Sample',_links=[link('customer','Customer')])
        self.m.guard_document(d)
        for doctype in ['Sales Invoice','Purchase Invoice','Payment Entry','Stock Entry','Sales Order']:
            with self.assertRaises(ValueError):self.m.block_submission(Document(doctype,company=self.m.COMPANY))

    def test_practice_company_cannot_be_given_real_tax_identity_or_credentials(self):
        with self.assertRaises(ValueError):self.m.guard_document(Document('Company',company_name=self.m.COMPANY,tax_id='real-vat'))
        d=Document('Company',company_name=self.m.COMPANY,custom_zatca_key='secret')
        d.meta.fields=[types.SimpleNamespace(fieldname='custom_zatca_key')]
        with self.assertRaises(ValueError):self.m.guard_document(d)
        with self.assertRaises(ValueError):self.m.guard_document(Document('ZATCA Settings',company=self.m.COMPANY))

    def test_demo_master_cannot_be_given_real_company_defaults(self):
        child=Document('Item Default',company='Real Company',_links=[link('company','Company')])
        with self.assertRaises(ValueError):self.m.guard_document(Document('Item',name='YOUSR-DEMO-DESK',item_code='YOUSR-DEMO-DESK',_children=[child]))

    def test_shared_price_lists_cannot_mix(self):
        d=Document('Item Price',item_code='YOUSR-DEMO-DESK',price_list='Standard Selling',_links=[link('item_code','Item'),link('price_list','Price List')])
        with self.assertRaises(ValueError):self.m.guard_document(d)
        d.values['price_list']='YOUSR-DEMO-Selling'
        self.m.guard_document(d)

    def test_demo_rename_merge_and_label_removal_are_blocked(self):
        with self.assertRaises(ValueError):self.m.protect_rename(Document('Customer',name='YOUSR-DEMO-Sample'),None,'old','new',True)
        with self.assertRaises(ValueError):self.m.guard_document(Document('Customer',name='YOUSR-DEMO-Sample',customer_name='Real customer'))
        self.m.protect_rename(Document('Customer',name='Real Customer'),None,'Real Customer','Different Real Customer',False)

    def test_inserts_force_namespaced_names_even_with_customer_naming_series(self):
        doc=types.SimpleNamespace(name='YOUSR-DEMO-Sample',insert=Mock())
        self.frappe.get_doc=Mock(return_value=doc)
        state=types.SimpleNamespace(records='[]',save=Mock())
        self.m._insert(state,'Customer',{'customer_name':'YOUSR-DEMO-Sample'})
        doc.insert.assert_called_once_with(ignore_permissions=True,set_name='YOUSR-DEMO-Sample')
        self.assertIn('YOUSR-DEMO-Sample',state.records)

    def test_ready_or_unrequested_demo_job_does_nothing(self):
        state=types.SimpleNamespace(status='Ready')
        self.frappe.get_single.return_value=state
        self.frappe.cache=types.SimpleNamespace(lock=Mock(return_value=unittest.mock.MagicMock()))
        self.m.create_demo()
        self.frappe.db.exists.assert_not_called()

if __name__=='__main__':unittest.main()
