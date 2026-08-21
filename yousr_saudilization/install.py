import frappe


def after_install():
    app_logo = "/assets/yousr_saudilization/images/login-logo.png"
    website_logo = "/assets/yousr_saudilization/images/website-logo.png"
    favicon = "/assets/yousr_saudilization/images/favicon.png"
    splash_logo = "/assets/yousr_saudilization/images/desk-logo.png"

    # Website Settings
    ws = frappe.get_single("Website Settings")
    ws.app_logo = website_logo
    ws.banner_image = website_logo
    ws.banner_valid = 1              
    ws.favicon = favicon
    ws.splash_image = splash_logo
    ws.app_name = "YousrERP"  
    ws.save(ignore_permissions=True)

    # Navbar Settings
    ns = frappe.get_single("Navbar Settings")
    ns.app_logo = app_logo
    ns.save(ignore_permissions=True)

    frappe.db.commit()

def after_uninstall():
    # Website Settings images remove 
    ws = frappe.get_single("Website Settings")
    ws.app_logo = None
    ws.banner_image = None
    ws.banner_valid = 0 
    ws.favicon = None
    ws.splash_image = None
    ws.app_name = ""  
    ws.save(ignore_permissions=True)

    # remove Navbar Settings 
    ns = frappe.get_single("Navbar Settings")
    ns.app_logo = None
    ns.save(ignore_permissions=True)

    frappe.db.commit()
