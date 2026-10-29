"""Safety checks for idempotent updates without a running Frappe site."""
import importlib
import sys
import types
import unittest

class Doc:
    def __init__(self, **values):
        self.values = values
        self.meta = types.SimpleNamespace(has_field=lambda f: f in values)
        self.saves = 0
    def get(self, f): return self.values.get(f)
    def set(self, f, v): self.values[f] = v
    def save(self, **kwargs): self.saves += 1

class BrandingTest(unittest.TestCase):
    def setUp(self):
        self.docs = {'Website Settings': Doc(app_name='YousrERP',app_logo='/assets/yousr_saudilization/images/website-logo.png',banner_image='/files/tenant.svg',favicon='',splash_image=''), 'Navbar Settings': Doc(app_logo='/files/customer-logo.svg')}
        sys.modules['frappe'] = types.SimpleNamespace(get_single=lambda name:self.docs[name],clear_cache=lambda:None)
        sys.modules.pop('yousr_saudilization.branding',None)
        self.branding = importlib.import_module('yousr_saudilization.branding')
    def test_migration_updates_owned_assets_and_preserves_tenant_choices(self):
        self.branding.apply_branding()
        self.assertTrue(self.docs['Website Settings'].get('app_logo').endswith('yousrerp-square-light.svg'))
        self.assertEqual('/files/tenant.svg',self.docs['Website Settings'].get('banner_image'))
        self.assertEqual('/files/customer-logo.svg',self.docs['Navbar Settings'].get('app_logo'))
        self.branding.apply_branding()
        self.assertEqual(1,self.docs['Website Settings'].saves)
        self.assertEqual(0,self.docs['Navbar Settings'].saves)
    def test_uninstall_preserves_replacement_logo_and_custom_name(self):
        self.docs['Website Settings'].set('app_name','Tenant ERP')
        self.branding.apply_branding(); self.branding.remove_owned_branding()
        self.assertEqual('Tenant ERP',self.docs['Website Settings'].get('app_name'))
        self.assertEqual('/files/tenant.svg',self.docs['Website Settings'].get('banner_image'))
        self.assertEqual('/files/customer-logo.svg',self.docs['Navbar Settings'].get('app_logo'))
        self.assertIsNone(self.docs['Website Settings'].get('app_logo'))

if __name__ == '__main__': unittest.main()
