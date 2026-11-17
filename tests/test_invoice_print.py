import base64
import importlib
import json
import sys
import types
import unittest
from datetime import date, time
from unittest.mock import Mock, patch
from pathlib import Path

class D(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__

class InvoicePrintTests(unittest.TestCase):
    def setUp(self):
        self.doc = D(doctype='Sales Invoice', name='INV-1', company='شركة اختبار', docstatus=0,
                     posting_date='2026-11-17', posting_time='10:00:00', grand_total=115,
                     total_taxes_and_charges=15, check_permission=Mock())
        self.settings = None
        self.phase2 = False
        self.rows = []
        self.signed = D(qr_code='SIGNED-PHASE2',integration_status='Accepted')
        self.vat = '311111111111113'
        self.available = True
        self.frappe = types.ModuleType('frappe')
        self.frappe.db = Mock()
        self.frappe.db.exists.side_effect = lambda dt, value: self.available if dt=='DocType' and value not in ['Sales Invoice','Print Format'] else (self.phase2 if dt=='ZATCA Business Settings' else True)
        self.frappe.db.get_value.side_effect = lambda dt,*a,**kw: self.settings if dt=='ZATCA Phase 1 Business Settings' else self.vat
        self.frappe.get_all = Mock(side_effect=lambda *a,**kw:self.rows)
        self.frappe.get_doc = Mock(side_effect=lambda dt,name:self.doc if dt=='Sales Invoice' else self.signed)
        self.frappe.get_meta = Mock(return_value=D(default_print_format='Sales Invoice Classic'))
        self.frappe.db.get_default.return_value = None
        utils=types.ModuleType('frappe.utils')
        utils.getdate=lambda v:date.fromisoformat(v)
        utils.get_time=lambda v:time.fromisoformat(v)
        utils.get_system_timezone=lambda:'Asia/Riyadh'
        self.modules=patch.dict(sys.modules, {'frappe':self.frappe,'frappe.utils':utils})
        self.modules.start();sys.modules.pop('yousr_saudilization.invoice_print',None)
        self.m=importlib.import_module('yousr_saudilization.invoice_print')
        self.png=patch.object(self.m,'_png',side_effect=lambda payload:'PNG:'+payload);self.png.start()
    def tearDown(self):
        self.png.stop();self.modules.stop();sys.modules.pop('yousr_saudilization.invoice_print',None)
    def test_phase1_live_values_utf8_lengths_and_riyadh_timezone(self):
        r=self.m.yousr_invoice_qr(self.doc);raw=base64.b64decode(r['src'][4:]);vals={};i=0
        while i<len(raw):
            tag,n=raw[i:i+2];vals[tag]=raw[i+2:i+2+n].decode();i+=n+2
        self.assertEqual({1:'شركة اختبار',2:self.vat,3:'2026-11-17T10:00:00+03:00',4:'115.00',5:'15.00'},vals)
        self.doc.grand_total=230;self.assertNotEqual(r,self.m.yousr_invoice_qr(self.doc))
        self.doc.check_permission.assert_called_with('read')
    def test_phase1_settings_override_company_vat_and_disabled_respected(self):
        self.settings=D(status='Disabled',vat_registration_number=self.vat)
        self.assertIsNone(self.m.yousr_invoice_qr(self.doc)['src'])
        self.settings.status='Active';self.assertEqual(1,self.m.yousr_invoice_qr(self.doc)['phase'])
    def test_missing_invalid_vat_does_not_invent_qr(self):
        for vat in ['', '123', '٣١١١١١١١١١١١١١٣', '111111111111111']:
            self.vat=vat;self.assertIsNone(self.m.yousr_invoice_qr(self.doc)['src'])
    def test_without_ksa_app_phase1_works_without_querying_absent_tables(self):
        self.available=False;self.assertEqual(1,self.m.yousr_invoice_qr(self.doc)['phase']);self.frappe.get_all.assert_not_called()
    def test_phase2_draft_never_gets_phase1_replacement(self):
        self.phase2=True;r=self.m.yousr_invoice_qr(self.doc);self.assertEqual(2,r['phase']);self.assertIsNone(r['src'])
    def test_phase2_uses_actual_signed_payload_and_exact_invoice_type(self):
        self.doc.docstatus=1;self.rows=[D(name='SIAF-1')]
        r=self.m.yousr_invoice_qr(self.doc);self.assertEqual('PNG:SIGNED-PHASE2',r['src'])
        kw=self.frappe.get_all.call_args.kwargs;self.assertEqual({'sales_invoice':'INV-1','invoice_doctype':'Sales Invoice'},kw['filters'])
    def test_historical_phase2_qr_retained_even_when_current_integration_disabled(self):
        self.doc.docstatus=1;self.rows=[D(name='SIAF-1')];self.assertEqual(2,self.m.yousr_invoice_qr(self.doc)['phase'])
    def test_rejected_retry_and_missing_phase2_payload_never_fall_back(self):
        self.doc.docstatus=1;self.rows=[D(name='SIAF-1')]
        for status in ['Rejected','Corrected','Resend']:
            self.signed.integration_status=status;self.assertIsNone(self.m.yousr_invoice_qr(self.doc)['src'])
        self.signed.integration_status='Accepted';self.signed.qr_code=None;self.assertIsNone(self.m.yousr_invoice_qr(self.doc)['src'])
    def test_unsaved_cancelled_and_unauthorized_invoice(self):
        self.assertIsNone(self.m.yousr_invoice_qr(D(doctype='Sales Invoice'))['src'])
        self.doc.docstatus=2;self.assertIsNone(self.m.yousr_invoice_qr(self.doc)['src'])
        self.doc.docstatus=0;self.doc.check_permission.side_effect=PermissionError
        with self.assertRaises(PermissionError):self.m.yousr_invoice_qr(self.doc)
    def test_canonical_document_prevents_forged_values(self):
        r=self.m.yousr_invoice_qr(D(doctype='Sales Invoice',name='INV-1',company='OTHER',grand_total=999));self.assertNotIn('OTHER',r['src'])
        self.frappe.get_doc.assert_called_with('Sales Invoice','INV-1')
    def test_default_install_idempotency_preserves_custom_choice_and_uninstall(self):
        module=types.ModuleType('frappe.custom.doctype.property_setter.property_setter');module.make_property_setter=Mock()
        with patch.dict(sys.modules,{'frappe.custom.doctype.property_setter.property_setter':module}):
            self.m.configure_default();module.make_property_setter.assert_called_once();self.frappe.db.set_default.assert_called_once()
            module.make_property_setter.reset_mock();self.frappe.get_meta.return_value.default_print_format=self.m.FORMAT
            self.m.configure_default();module.make_property_setter.assert_not_called()
            self.frappe.db.get_default.return_value=json.dumps({'previous':'Standard'});self.m.remove_owned_default()
            self.assertEqual('Standard',module.make_property_setter.call_args.args[3])
            module.make_property_setter.reset_mock();self.frappe.get_meta.return_value.default_print_format='Client Custom'
            self.m.configure_default();self.m.remove_owned_default();module.make_property_setter.assert_not_called()
    def test_template_has_no_customer_snapshots_and_handles_free_text_services(self):
        p=Path(__file__).resolve().parents[1]/'yousr_saudilization/yousr_saudilization/print_format/saudilization_sales_invoice/saudilization_sales_invoice.json'
        x=json.loads(p.read_text());self.assertIn('yousr_invoice_qr(doc)',x['html']);self.assertNotIn('saved_qrs',x['html']);self.assertNotIn('ACC-SINV-2026-',x['html']);self.assertNotIn('30 days',x['html']);self.assertIn('else (item.item_name or item.description',x['html'])

if __name__=='__main__':unittest.main()
