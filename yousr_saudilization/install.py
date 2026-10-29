from yousr_saudilization.branding import apply_branding, remove_owned_branding


def after_install():
    apply_branding()


def after_uninstall():
    remove_owned_branding()
