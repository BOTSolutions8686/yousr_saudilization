"""Small, authenticated presentation context for the native setup wizard.

No accounts, companies, permissions or accounting records are created here.
"""
import json
import frappe

PORTALS = {"https://yousrerp.com", "https://stage.yousrerp.com"}
INDUSTRIES = {"Manufacturing", "Retail", "Wholesale / Distribution", "E-commerce", "Services / Consulting", "Construction / Real Estate", "Technology / Software", "Healthcare", "Education", "Agriculture", "Food & Beverage", "Non Profit", "Other"}


def _context():
    value = frappe.conf.get("yousr_onboarding_context") or {}
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (ValueError, TypeError):
            value = {}
    return value if isinstance(value, dict) else {}


def _text(value, limit):
    return value.strip()[:limit] if isinstance(value, str) else ""


def boot_session(bootinfo):
    """Brand presentation only; preserve native routes, validation and identities."""
    if frappe.session.user == "Guest":
        return
    context = _context()
    portal = _text(context.get("portal_url"), 100).rstrip("/")
    if portal not in PORTALS:
        portal = "https://yousrerp.com"
    setup_complete = bool(frappe.is_setup_complete())
    admin = frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles()
    ui = {
        "portal_url": portal,
        "help_url": portal + "/help-and-sessions",
    }
    if not setup_complete and admin:
        ui.update({
            "full_name": _text(context.get("full_name"), 100),
            "company_name": _text(context.get("company_name"), 140),
            "email": _text(context.get("email"), 140) if context.get("email_verified") is True else "",
            "industry": context.get("industry") if context.get("industry") in INDUSTRIES else "",
        })
    # New managed workspaces do not send upstream diagnostics by default.
    # Existing configured tenants without this context retain their prior preference.
    if (not setup_complete or context.get("managed_setup") is True) and not frappe.conf.get("yousr_external_diagnostics_enabled"):
        bootinfo["enable_telemetry"] = False
    bootinfo["yousr_setup"] = ui
    # v16's apps screen reads app_data; keep native permission and route metadata.
    ar = str(bootinfo.get("lang") or "en").startswith("ar")
    for app in bootinfo.get("app_data") or []:
        name = app.get("app_name")
        title = app.get("app_title")
        if name == "erpnext" and title in {"ERPNext", "" , None}:
            app["app_title"] = "YousrERP"
        elif name == "frappe" and title in {"Framework", "Frappe Framework", "Frappe", "", None}:
            app["app_title"] = "إعدادات مساحة العمل" if ar else "Workspace settings"
        elif name == "hrms" and title in {"Frappe HR", "HRMS", "HR", "", None}:
            app["app_title"] = "الموارد البشرية والرواتب" if ar else "People & payroll"
        logo = app.get("app_logo_url") or ""
        defaults = {"/assets/erpnext/images/erpnext-logo.svg", "/assets/frappe/images/frappe-framework-logo.svg", "/assets/frappe/images/frappe-logo.svg", "/assets/hrms/images/frappe-hr-logo.svg"}
        if not logo or logo in defaults:
            asset = {"erpnext":"yousrerp-favicon.svg", "frappe":"yousrerp-settings.svg", "hrms":"yousrerp-people.svg"}.get(name)
            if asset:
                app["app_logo_url"] = "/assets/yousr_saudilization/images/" + asset

    for app in (bootinfo.get("apps_data") or {}).get("apps", []):
        if app.get("name") == "erpnext":
            app["title"] = "YousrERP"
            if app.get("logo") in {"/assets/erpnext/images/erpnext-logo.svg", "", None}:
                app["logo"] = "/assets/yousr_saudilization/images/yousrerp-favicon.svg"
            app["setup_wizard_text"] = "Your workspace is ready. Let’s make it yours."
        elif app.get("name") == "hrms":
            app["title"] = "People & payroll"


def prepare_new_workspace():
    """Default external diagnostics off only before first setup; preserve established tenant choices."""
    if frappe.is_setup_complete():
        return
    settings = frappe.get_single("System Settings")
    if settings.meta.has_field("enable_telemetry") and settings.get("enable_telemetry"):
        # A fresh site has no language/time zone yet. Do not save the whole
        # mandatory setup document merely to change this one boolean preference.
        frappe.db.set_single_value("System Settings", "enable_telemetry", 0)
