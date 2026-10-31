"""Stop workspace RPCs from opening provider billing; ERP accounting is separate."""
import frappe

@frappe.whitelist()
def unavailable(*args, **kwargs):
    lang = str(getattr(frappe.local, "lang", "en"))
    message = ("أدر الاشتراكات والفوترة من حسابك في YousrERP." if lang.startswith("ar")
               else "Manage subscriptions and billing in your YousrERP account.")
    frappe.throw(message, frappe.PermissionError)
