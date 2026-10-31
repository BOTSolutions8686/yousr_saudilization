"""Small, authenticated presentation context for the native setup wizard.

No accounts, companies, permissions or accounting records are created here.
"""
import json
import frappe

PORTALS = {"https://yousrerp.com", "https://stage.yousrerp.com"}
INDUSTRIES = {"Manufacturing", "Retail", "Wholesale / Distribution", "E-commerce", "Services / Consulting", "Construction / Real Estate", "Technology / Software", "Healthcare", "Education", "Agriculture", "Food & Beverage", "Non Profit", "Other"}
TASKS = {"sales", "stock", "purchasing", "accounting", "projects", "manufacturing", "hr"}


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
    setup_complete = bool(bootinfo.get("setup_complete", (bootinfo.get("sysdefaults") or {}).get("setup_complete", False)))
    admin = frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles()
    ui = {
        "portal_url": portal,
        "help_url": portal + "/help-and-sessions",
        "first_task": context.get("first_task") if context.get("first_task") in TASKS else "sales",
        "show_first_task": context.get("show_first_task") is True,
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
