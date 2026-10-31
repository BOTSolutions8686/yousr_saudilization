"""Boundary checks for setup-only context and native privilege preservation."""
import importlib
import sys
import types
import unittest

class OnboardingTest(unittest.TestCase):
    def load(self, context=None, user='Administrator', roles=None, complete=False):
        sys.modules['frappe'] = types.SimpleNamespace(conf={'yousr_onboarding_context':context or {}}, session=types.SimpleNamespace(user=user), get_roles=lambda:roles or [], is_setup_complete=lambda:complete)
        sys.modules.pop('yousr_saudilization.onboarding',None)
        module=importlib.import_module('yousr_saudilization.onboarding')
        boot={'setup_complete':complete, 'enable_telemetry':True, 'apps_data':{'apps':[{'name':'erpnext','title':'ERPNext','logo':'/assets/erpnext/images/erpnext-logo.svg'}]}}
        module.boot_session(boot)
        return boot

    def test_unverified_email_and_unsafe_portal_are_not_exposed(self):
        boot=self.load({'email':'private@example.invalid','email_verified':False,'portal_url':'https://evil.invalid','industry':'arbitrary','company_name':' Demo '})
        self.assertEqual('',boot['yousr_setup']['email'])
        self.assertEqual('https://yousrerp.com',boot['yousr_setup']['portal_url'])
        self.assertEqual('',boot['yousr_setup']['industry'])
        self.assertEqual('Demo',boot['yousr_setup']['company_name'])
        self.assertFalse(boot['enable_telemetry'])
        self.assertEqual('erpnext',boot['apps_data']['apps'][0]['name'])
        self.assertEqual('YousrERP',boot['apps_data']['apps'][0]['title'])

    def test_only_verified_contact_is_prefilled_for_workspace_admin(self):
        boot=self.load({'email':'owned@example.invalid','email_verified':True,'portal_url':'https://stage.yousrerp.com','industry':'Retail'})
        self.assertEqual('owned@example.invalid',boot['yousr_setup']['email'])
        self.assertEqual('Retail',boot['yousr_setup']['industry'])
        self.assertEqual('https://stage.yousrerp.com/help-and-sessions',boot['yousr_setup']['help_url'])

    def test_guests_and_regular_staff_do_not_receive_owner_profile(self):
        self.assertNotIn('yousr_setup',self.load({'full_name':'Owner'},user='Guest'))
        boot=self.load({'full_name':'Owner','email':'owner@example.invalid','email_verified':True},user='staff@example.invalid')
        self.assertNotIn('full_name',boot['yousr_setup'])
        self.assertNotIn('email',boot['yousr_setup'])

    def test_two_workspaces_keep_their_company_context_separate(self):
        first=self.load({'company_name':'Company A','full_name':'Same Owner','email':'personal@example.invalid','email_verified':True})
        second=self.load({'company_name':'Company B','full_name':'Same Owner','email':'personal@example.invalid','email_verified':True})
        self.assertEqual('Company A',first['yousr_setup']['company_name'])
        self.assertEqual('Company B',second['yousr_setup']['company_name'])
        self.assertEqual('personal@example.invalid',first['yousr_setup']['email'])

    def test_authoritative_completed_state_preserves_existing_tenant_even_during_partial_boot(self):
        self.load(complete=True)
        module=sys.modules['yousr_saudilization.onboarding']
        boot={'sysdefaults':{'setup_complete':False},'enable_telemetry':True}
        module.boot_session(boot)
        self.assertTrue(boot['enable_telemetry'])
        self.assertNotIn('company_name',boot['yousr_setup'])

    def test_existing_configured_tenant_keeps_telemetry_preference_and_custom_icon(self):
        boot=self.load(complete=True)
        self.assertTrue(boot['enable_telemetry'])
        self.assertNotIn('company_name',boot['yousr_setup'])

    def test_new_workspace_diagnostics_default_does_not_change_established_tenants(self):
        self.load()
        module=sys.modules['yousr_saudilization.onboarding']
        calls=[]
        settings=types.SimpleNamespace(meta=types.SimpleNamespace(has_field=lambda field:True),get=lambda field:1,set=lambda field,value:calls.append((field,value)),save=lambda **kwargs:calls.append('saved'))
        module.frappe.is_setup_complete=lambda:False
        module.frappe.get_single=lambda name:settings
        module.frappe.db=types.SimpleNamespace(set_single_value=lambda doctype,field,value:calls.append((doctype,field,value)))
        module.prepare_new_workspace()
        self.assertEqual([('System Settings','enable_telemetry',0)],calls)
        calls.clear()
        module.frappe.is_setup_complete=lambda:True
        module.prepare_new_workspace()
        self.assertEqual([],calls)

    def test_native_setup_loader_receives_plain_javascript_asset_path(self):
        from pathlib import Path
        import ast
        tree=ast.parse((Path(__file__).parents[1]/'yousr_saudilization/hooks.py').read_text())
        assignment=next(node for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='setup_wizard_requires' for target in node.targets))
        path=ast.literal_eval(assignment.value)
        self.assertTrue(path.endswith('.js'))
        self.assertNotIn('?',path)

    def test_erp_yes_no_boot_label_does_not_hide_new_company_suggestions(self):
        self.load({'company_name':'Company A'},complete=False)
        module=sys.modules['yousr_saudilization.onboarding']
        # ERP's earlier boot hook uses the string "No", which is truthy in Python.
        boot={'setup_complete':'No','sysdefaults':{'setup_complete':False}}
        module.boot_session(boot)
        self.assertEqual('Company A',boot['yousr_setup']['company_name'])
        self.assertEqual('',boot['yousr_setup']['email'])

    def test_v16_app_cards_keep_permissions_and_routes_while_branding_default_names(self):
        self.load(complete=True)
        module=sys.modules['yousr_saudilization.onboarding']
        apps=[{'app_name':'erpnext','app_title':'ERPNext','app_logo_url':'/assets/erpnext/images/erpnext-logo.svg','on_apps_screen':True,'app_route':'/desk/setup/home'}, {'app_name':'frappe','app_title':'Framework','on_apps_screen':False,'dock':[]}, {'app_name':'hrms','app_title':'Frappe HR','on_apps_screen':True}]
        boot={'lang':'en','app_data':apps}
        module.boot_session(boot)
        self.assertEqual('YousrERP',apps[0]['app_title'])
        self.assertEqual('/desk/setup/home',apps[0]['app_route'])
        self.assertFalse(apps[1]['on_apps_screen'])
        self.assertEqual([],apps[1]['dock'])
        self.assertEqual('Workspace settings',apps[1]['app_title'])
        self.assertEqual('People & payroll',apps[2]['app_title'])
        self.assertNotIn('show_first_task',boot['yousr_setup'])

    def test_tenant_custom_app_title_and_logo_are_preserved(self):
        self.load(complete=True)
        module=sys.modules['yousr_saudilization.onboarding']
        app={'app_name':'erpnext','app_title':'My business','app_logo_url':'/files/tenant.svg','on_apps_screen':True}
        module.boot_session({'app_data':[app]})
        self.assertEqual('My business',app['app_title'])
        self.assertEqual('/files/tenant.svg',app['app_logo_url'])

    def test_list_valued_hook_icons_do_not_break_boot_or_rebrand_unrelated_plugins(self):
        self.load(complete=True)
        module=sys.modules['yousr_saudilization.onboarding']
        plugin={'app_name':'ksa_compliance','app_title':'Saudi e-invoicing','app_logo_url':['/assets/frappe/images/frappe-framework-logo.svg'],'on_apps_screen':False}
        erp={'app_name':'erpnext','app_title':'ERPNext','app_logo_url':['/assets/erpnext/images/erpnext-logo.svg']}
        module.boot_session({'app_data':[plugin,erp]})
        self.assertEqual(['/assets/frappe/images/frappe-framework-logo.svg'],plugin['app_logo_url'])
        self.assertEqual('/assets/yousr_saudilization/images/yousrerp-favicon.svg',erp['app_logo_url'])

if __name__=='__main__':unittest.main()
