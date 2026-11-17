from yousr_saudilization.branding import apply_branding, remove_owned_branding


def after_install():
    apply_branding()
    from yousr_saudilization.onboarding import prepare_new_workspace
    prepare_new_workspace()
    from yousr_saudilization.invoice_print import configure_default
    configure_default()


def after_uninstall():
    remove_owned_branding()
    from yousr_saudilization.invoice_print import remove_owned_default
    remove_owned_default()
