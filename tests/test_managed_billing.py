import importlib
import sys
import types
import unittest

class BillingBlocked(Exception): pass

class ManagedBillingTest(unittest.TestCase):
    def test_provider_billing_shortcuts_stop_before_credentials_or_network_access(self):
        def throw(message, exception): raise exception(message)
        sys.modules['frappe']=types.SimpleNamespace(whitelist=lambda **kwargs:lambda fn:fn,local=types.SimpleNamespace(lang='en'),throw=throw,PermissionError=BillingBlocked)
        sys.modules.pop('yousr_saudilization.managed_billing',None)
        module=importlib.import_module('yousr_saudilization.managed_billing')
        with self.assertRaisesRegex(BillingBlocked,'YousrERP account'):
            module.unavailable(method='site.info',data={})
        module.frappe.local.lang='ar'
        with self.assertRaisesRegex(BillingBlocked,'YousrERP'):
            module.unavailable()

    def test_hooks_target_provider_billing_without_replacing_setup_or_erp_accounting(self):
        hooks=importlib.import_module('yousr_saudilization.hooks')
        mappings=hooks.override_whitelisted_methods
        self.assertEqual(18,len(mappings))
        self.assertIn('frappe.integrations.frappe_providers.frappecloud_billing.api',mappings)
        self.assertIn('frappe.integrations.frappe_providers.cloud_settings.change_plan',mappings)
        self.assertTrue(all(path.startswith('frappe.integrations.frappe_providers.') for path in mappings))
        self.assertTrue(all(target=='yousr_saudilization.managed_billing.unavailable' for target in mappings.values()))
        self.assertFalse(any('setup_wizard' in path or 'sales_invoice' in path or path.endswith('is_fc_site') for path in mappings))

if __name__=='__main__':unittest.main()
