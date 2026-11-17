"""Read-only, phase-aware invoice printing. Never signs/submits or alters invoices."""
import base64
import json
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from zoneinfo import ZoneInfo

import frappe

FORMAT = "Saudilization Sales Invoice"
_BACKUP_KEY = "yousr_invoice_print_default_before"
_OWNED_DEFAULTS = {"", "Standard", FORMAT, "ZATCA Phase 1 Print Format", "ZATCA Phase 2 Print Format", "Saudilization Sales Invoice - Nawaf Phase 1"}


def configure_default():
    """Install an app default, retaining a tenant's explicitly selected custom format."""
    if not frappe.db.exists("DocType", "Sales Invoice") or not frappe.db.exists("Print Format", FORMAT):
        return
    current = frappe.get_meta("Sales Invoice").default_print_format or ""
    if current == FORMAT or current not in _OWNED_DEFAULTS:
        return
    from frappe.custom.doctype.property_setter.property_setter import make_property_setter
    if not frappe.db.get_default(_BACKUP_KEY):
        frappe.db.set_default(_BACKUP_KEY, json.dumps({"previous": current}))
    make_property_setter("Sales Invoice", None, "default_print_format", FORMAT, "Data", for_doctype=True)


def remove_owned_default():
    if not frappe.db.exists("DocType", "Sales Invoice"):
        return
    if (frappe.get_meta("Sales Invoice").default_print_format or "") != FORMAT:
        return
    previous = json.loads(frappe.db.get_default(_BACKUP_KEY) or '{"previous":""}')["previous"]
    from frappe.custom.doctype.property_setter.property_setter import make_property_setter
    make_property_setter("Sales Invoice", None, "default_print_format", previous, "Data", for_doctype=True)


def _png(payload):
    import pyqrcode
    buffer = BytesIO()
    pyqrcode.create(payload).png(buffer, scale=6)
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def _phase1_payload(doc, vat):
    # Frappe stores posting date/time in the site's timezone, not the worker's timezone.
    from frappe.utils import getdate, get_time, get_system_timezone
    stamp = datetime.combine(getdate(doc.posting_date), get_time(doc.posting_time))
    stamp = stamp.replace(tzinfo=ZoneInfo(get_system_timezone())).isoformat(timespec="seconds")
    values = [doc.company, vat, stamp, format(Decimal(str(doc.grand_total)), '.2f'),
              format(Decimal(str(doc.total_taxes_and_charges)), '.2f')]
    raw = bytearray()
    for tag, value in enumerate(values, 1):
        encoded = value.encode("utf-8")
        if len(encoded) > 255:
            raise ValueError("QR field exceeds Phase 1 TLV length")
        raw.extend(bytes((tag, len(encoded))))
        raw.extend(encoded)
    return base64.b64encode(raw).decode("ascii")


def yousr_invoice_qr(doc):
    """Jinja helper. Canonical saved invoice only; no network, writes, or cached QR snapshots."""
    empty = {"src": None, "phase": None, "message": "QR unavailable: complete the company tax settings."}
    if doc.get("doctype") != "Sales Invoice" or not doc.get("name"):
        return empty
    invoice = frappe.get_doc("Sales Invoice", doc.name)
    invoice.check_permission("read")
    if invoice.docstatus == 2:
        return {**empty, "message": "Cancelled invoice"}
    # An existing Phase 2 record is authoritative, including pending/rejected records.
    # Never replace its signed payload with a five-field Phase 1 QR.
    siaf_rows = frappe.get_all("Sales Invoice Additional Fields", filters={
        "sales_invoice": invoice.name, "invoice_doctype": "Sales Invoice"},
        fields=["name"], order_by="creation desc", limit_page_length=1) if frappe.db.exists("DocType", "Sales Invoice Additional Fields") else []
    phase2 = frappe.db.exists("ZATCA Business Settings", {
        "company": invoice.company, "enable_zatca_integration": 1}) if frappe.db.exists("DocType", "ZATCA Business Settings") else False
    if siaf_rows or phase2:
        result = {**empty, "phase": 2, "message": "Phase 2 QR is available after invoice signing."}
        if not siaf_rows or invoice.docstatus != 1:
            return result
        signed = frappe.get_doc("Sales Invoice Additional Fields", siaf_rows[0].name)
        if signed.integration_status in {"Rejected", "Corrected", "Resend"}:
            return {**result, "message": "Phase 2 invoice requires review: " + signed.integration_status}
        if signed.qr_code:
            return {"src": _png(signed.qr_code), "phase": 2, "message": ""}
        return result
    settings = frappe.db.get_value("ZATCA Phase 1 Business Settings", {"company": invoice.company},
                                   ["status", "vat_registration_number"], as_dict=True) if frappe.db.exists("DocType", "ZATCA Phase 1 Business Settings") else None
    if settings and settings.status != "Active":
        return {**empty, "phase": 1, "message": "Phase 1 company settings are disabled."}
    vat = (settings.vat_registration_number if settings else
           frappe.db.get_value("Company", invoice.company, "tax_id")) or ""
    vat = vat.strip()
    if len(vat) != 15 or not vat.isascii() or not vat.isdigit() or vat[0] != '3' or vat[-1] != '3':
        return {**empty, "phase": 1}
    try:
        return {"src": _png(_phase1_payload(invoice, vat)), "phase": 1, "message": ""}
    except (ValueError, TypeError):
        return {**empty, "phase": 1, "message": "QR unavailable: check invoice date, time and totals."}
