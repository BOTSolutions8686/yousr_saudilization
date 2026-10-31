from yousr_saudilization.branding import apply_branding, remove_owned_branding


def after_install():
    apply_branding()
    from yousr_saudilization.onboarding import prepare_new_workspace
    prepare_new_workspace()


def after_uninstall():
    remove_owned_branding()
