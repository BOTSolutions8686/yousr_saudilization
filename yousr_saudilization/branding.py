"""Idempotent branding updates which preserve tenant-selected settings."""
import frappe

ASSETS = "/assets/yousr_saudilization/images/"
LEGACY = {ASSETS + n for n in ("login-logo.png", "website-logo.png", "desk-logo.png", "favicon.png")}
SETTING_VALUES = {
    "Website Settings": {
        "app_name": "YousrERP",
        "app_logo": ASSETS + "yousrerp-square-light.svg",
        "banner_image": ASSETS + "yousrerp-compact-light.svg",
        "favicon": ASSETS + "yousrerp-favicon.svg",
        "splash_image": ASSETS + "yousrerp-square-light.svg",
    },
    "Navbar Settings": {"app_logo": ASSETS + "yousrerp-compact-light.svg"},
}

def is_owned_or_empty(value):
    return not value or value in LEGACY or str(value).startswith(ASSETS + "yousrerp-") or value in {"YousrERP", "Frappe", "ERPNext"}

def apply_branding():
    """Update only blank or this app's own values. Never overwrite a tenant logo."""
    for doctype, values in SETTING_VALUES.items():
        doc = frappe.get_single(doctype)
        changed = False
        for field, value in values.items():
            if doc.meta.has_field(field) and is_owned_or_empty(doc.get(field)) and doc.get(field) != value:
                doc.set(field, value)
                changed = True
        if changed:
            doc.save(ignore_permissions=True)
    frappe.clear_cache()

def remove_owned_branding():
    """Uninstall clears this app's paths only, preserving later tenant branding."""
    for doctype, values in SETTING_VALUES.items():
        doc = frappe.get_single(doctype)
        changed = False
        for field in values:
            current = doc.get(field)
            if doc.meta.has_field(field) and current and is_owned_or_empty(current):
                doc.set(field, None)
                changed = True
        if changed:
            doc.save(ignore_permissions=True)
    frappe.clear_cache()
