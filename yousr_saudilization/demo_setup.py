"""Opt-in practice records. No invoice submission, credentials or external calls.

The practice company never becomes the default. Shared masters use a reserved
namespace and are prohibited in real-company transactions, in both directions.
"""
import json

import frappe
from frappe import _

STATE = "Yousr Demo Setup"
COMPANY = "Yousr Practice - DEMO"
PREFIX = "YOUSR-DEMO-"
ABBR = "YDEMO"
MASTER_KEYS = {"Item": "item_code", "Customer": "customer_name", "Supplier": "supplier_name",
               "Price List": "price_list_name", "Item Group": "item_group_name",
               "Customer Group": "customer_group_name", "Supplier Group": "supplier_group_name"}
MASTERS = set(MASTER_KEYS)
ALLOWED = {
    "Company", "Account", "Warehouse", "Cost Center", "Department",
    "Sales Taxes and Charges Template", "Purchase Taxes and Charges Template",
    "Mode of Payment Account", "Financial Report Template", "Quotation", "Sales Order",
    "Purchase Order", "Sales Invoice", "Purchase Invoice", "Delivery Note", "Purchase Receipt",
    "Stock Entry", "Journal Entry", "Payment Entry", "Budget", "Fiscal Year",
}


def _manager():
    if frappe.session.user == "Guest":
        frappe.throw(_("Please sign in."), frappe.PermissionError)
    frappe.only_for("System Manager")


def enabled():
    return frappe.conf.get("yousr_demo_enabled", True) not in (False, 0, "0")


def _state():
    return frappe.get_single(STATE)


def _manifest(state):
    return json.loads(state.records or "[]")


def _save(state):
    state.save(ignore_permissions=True)


def request_after_setup(args):
    """Success hook only; a demo problem must never undo native business setup."""
    if not enabled() or (args or {}).get("yousr_load_demo") not in (True, 1, "1"):
        return
    try:
        _manager()
        state = _state()
        if state.status:
            return
        real = (args or {}).get("company_name")
        if not real or real == COMPANY or not frappe.db.exists("Company", real):
            return
        if frappe.db.exists("Company", COMPANY):
            return  # Never adopt an unrelated company with the reserved name.
        state.real_company = real
        state.status = "Queued"
        state.records = "[]"
        _save(state)
        frappe.enqueue("yousr_saudilization.demo_setup.create_demo", queue="long",
                       enqueue_after_commit=True, job_id="yousr-optional-demo", timeout=300)
    except Exception:
        frappe.log_error(title="Optional Yousr practice setup could not be queued")


def _defaults():
    return (frappe.db.get_single_value("Global Defaults", "default_company"),
            frappe.defaults.get_global_default("company"))


def _insert(state, doctype, values):
    doc = frappe.get_doc({"doctype": doctype, **values})
    key = MASTER_KEYS.get(doctype)
    doc.insert(ignore_permissions=True, set_name=values[key] if key else None)
    if key and not doc.name.startswith(PREFIX):
        raise ValueError("practice_master_name_not_isolated")
    records = _manifest(state)
    records.append({"doctype": doctype, "name": doc.name})
    state.records = json.dumps(records)
    _save(state)
    return doc


def create_demo():
    """One atomic, serialized seed after native setup; never replay on Ready."""
    with frappe.cache.lock("yousr-optional-demo", timeout=330, blocking_timeout=1):
        state = _state()
        if not enabled() or state.status not in {"Queued", "Failed"}:
            return
        if not frappe.is_setup_complete() or not frappe.db.exists("Company", state.real_company):
            return
        frappe.db.savepoint("yousr_demo_seed")
        before = _defaults()
        try:
            if frappe.db.exists("Company", COMPANY) or _manifest(state):
                raise ValueError("reserved_practice_records_exist")
            state.status = "Building"
            _save(state)
            real = frappe.get_doc("Company", state.real_company)
            _insert(state, "Company", {"company_name": COMPANY, "abbr": ABBR,
                    "country": real.country, "default_currency": real.default_currency,
                    "chart_of_accounts": "Standard", "create_chart_of_accounts_based_on": "Standard Template"})
            for doctype, field, parent, root in [
                ("Item Group", "item_group_name", "parent_item_group", "All Item Groups"),
                ("Customer Group", "customer_group_name", "parent_customer_group", "All Customer Groups"),
                ("Supplier Group", "supplier_group_name", "parent_supplier_group", "All Supplier Groups"),
            ]:
                _insert(state, doctype, {field: PREFIX + doctype, parent: root, "is_group": 0})
            customer = _insert(state, "Customer", {"customer_name": PREFIX + "Sample Customer",
                    "customer_type": "Company", "customer_group": PREFIX + "Customer Group", "territory": "All Territories"})
            supplier = _insert(state, "Supplier", {"supplier_name": PREFIX + "Sample Supplier",
                    "supplier_type": "Company", "supplier_group": PREFIX + "Supplier Group"})
            for code, name in [("DESK", "Sample desk"), ("CHAIR", "Sample chair"), ("SERVICE", "Sample service")]:
                _insert(state, "Item", {"item_code": PREFIX + code, "item_name": "DEMO - " + name,
                        "item_group": PREFIX + "Item Group", "stock_uom": "Nos", "is_stock_item": 0,
                        "is_sales_item": 1, "is_purchase_item": 1,
                        "description": "Fictional practice item. Not for real business transactions."})
            _insert(state, "Price List", {"price_list_name": PREFIX + "Selling", "currency": real.default_currency,
                    "selling": 1, "buying": 0, "enabled": 1})
            _insert(state, "Price List", {"price_list_name": PREFIX + "Buying", "currency": real.default_currency,
                    "selling": 0, "buying": 1, "enabled": 1})
            quotation = _insert(state, "Quotation", {"company": COMPANY, "quotation_to": "Customer",
                    "party_name": customer.name, "currency": real.default_currency,
                    "selling_price_list": PREFIX + "Selling", "transaction_date": frappe.utils.today(),
                    "valid_till": frappe.utils.add_days(frappe.utils.today(), 30),
                    "items": [{"item_code": PREFIX + "DESK", "qty": 2, "rate": 100},
                              {"item_code": PREFIX + "CHAIR", "qty": 4, "rate": 50}],
                    "remarks": "DEMO ONLY - fictional draft. No real invoice or tax submission."})
            _insert(state, "Purchase Order", {"company": COMPANY, "supplier": supplier.name,
                    "currency": real.default_currency, "buying_price_list": PREFIX + "Buying",
                    "transaction_date": frappe.utils.today(), "schedule_date": frappe.utils.add_days(frappe.utils.today(), 7),
                    "items": [{"item_code": PREFIX + "DESK", "qty": 2, "rate": 70}],
                    "remarks": "DEMO ONLY - fictional draft. No supplier communication."})
            if before != _defaults():
                raise ValueError("practice_changed_default_company")
            state.status = "Ready"
            state.demo_company = COMPANY
            state.error_code = ""
            _save(state)
        except Exception:
            frappe.db.rollback(save_point="yousr_demo_seed")
            state = _state()
            state.status = "Failed"
            state.error_code = "practice_setup_failed"
            _save(state)
            frappe.log_error(title="Optional Yousr practice setup failed safely")


def _links(doc):
    for row in [doc, *doc.get_all_children()]:
        for field in row.meta.get_link_fields():
            value = row.get(field.fieldname)
            if value:
                target = row.get(field.options) if field.fieldtype == "Dynamic Link" else field.options
                yield target, value


def _reserved(value):
    return isinstance(value, str) and (value == COMPANY or value.startswith(PREFIX))


def guard_document(doc, method=None):
    """Ordinary records retain native handlers; only reserved practice links are constrained."""
    if doc.doctype == STATE:
        return
    company = doc.get("company")
    identity = doc.get("company_name" if doc.doctype == "Company" else MASTER_KEYS.get(doc.doctype, "name"))
    links = list(_links(doc))
    reserved = _reserved(doc.name) or _reserved(identity) or company == COMPANY or any(_reserved(v) for _, v in links)
    if not reserved:
        return
    if doc.doctype == "Company" and identity == COMPANY:
        if doc.get("tax_id"):
            frappe.throw(_("The practice company cannot have a VAT registration or live tax identity."))
        for field in doc.meta.fields:
            if any(word in field.fieldname.lower() for word in ("zatca", "csid", "private_key")) and doc.get(field.fieldname):
                frappe.throw(_("Do not connect the practice company to tax credentials. Use the labelled ZATCA examples."))
        return
    if doc.doctype in MASTERS and (_reserved(identity) or _reserved(doc.name)):
        if not _reserved(identity):
            frappe.throw(_("Practice masters must keep their DEMO identity."))
        if any(target == "Company" and value != COMPANY for target, value in links):
            frappe.throw(_("Practice masters cannot be assigned to a real company."))
        return
    if company == COMPANY:
        if doc.doctype not in ALLOWED:
            frappe.throw(_("This integration or document is not available in the practice company."))
        if any(target in MASTERS and not _reserved(value) for target, value in links):
            frappe.throw(_("Use only DEMO customers, suppliers, items and price lists in the practice company."))
        return
    if doc.doctype == "Item Price" and all(_reserved(v) for t, v in links if t in {"Item", "Price List"}):
        return
    frappe.throw(_("DEMO records cannot be used in your real company. Choose a real business record."))


def block_submission(doc, method=None):
    if doc.get("company") == COMPANY:
        frappe.throw(_("Practice documents stay as drafts. No accounting entries, payments or ZATCA submissions are made. Use your real company for live business."))


def protect_rename(doc, method=None, *args, **kwargs):
    if _reserved(doc.name) or doc.get("company") == COMPANY or any(_reserved(a) for a in args if isinstance(a, str)):
        frappe.throw(_("Practice records cannot be renamed or merged with real business records."))


@frappe.whitelist()
def status():
    _manager()
    state = _state()
    return {"status": state.status or "Not requested", "company": state.demo_company,
            "records": _manifest(state) if state.status == "Ready" else [],
            "error": state.error_code, "zatca_mode": "labelled_examples_only"}


@frappe.whitelist()
def retry():
    _manager()
    state = _state()
    if state.status != "Failed" or _manifest(state) or frappe.db.exists("Company", COMPANY):
        frappe.throw(_("This practice setup cannot be retried automatically. Please contact support."))
    state.status = "Queued"
    _save(state)
    frappe.enqueue("yousr_saudilization.demo_setup.create_demo", queue="long",
                   enqueue_after_commit=True, job_id="yousr-optional-demo", timeout=300)
    return {"status": "Queued"}
