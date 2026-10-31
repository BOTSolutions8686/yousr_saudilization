# YousrERP workspace welcome

The app extends the supported version-16 setup hooks. It preserves native account, company, chart, fiscal-year and module validation and save handlers. Four native steps remain: preferences, workspace contact, working style, company. Users submit setup themselves. The extension creates no invoices, payments or tax submissions.

Portal login identity and workspace identity are separate. Authenticated server context may suggest the current subscription’s business name and a verified portal email. Every suggestion remains editable. A phone-only account receives no invented email. A personal portal email may be replaced with a business email in the native workspace profile. No change is copied back to portal login or billing identity. No passwords, OTPs or VAT records are transported. Context is hidden from guests and ordinary workspace staff.

The portal must explicitly enable context transfer; existing deployments default off. The site config is scoped to the exact customer workspace. Two subscriptions belonging to one owner retain different company suggestions. No global portal billing identity or industry is substituted for a workspace’s information.

For a newly unconfigured workspace, external diagnostics default off. Established tenant settings are preserved. First-task help is optional, dismissible, and opens native forms without saving records or granting permissions. Its dismissal is scoped to this browser and workspace hostname.

Source names, licence notices, app identifiers and backend routes remain intact. Customer presentation uses YousrERP branding; tenant-selected logos remain their own. Core Frappe/ERPNext files are not patched.

Rollback: restore the previous app revision/image using a verified Cloud backup; disable portal context transfer. Do not delete companies or rewrite confirmed workspace identities to undo presentation changes.

Migration acceptance: fresh System Settings has no language/time zone until native setup. Set only the telemetry boolean using the single-value database API; never save the incomplete settings document or invent required preferences. Version0.2.0 migration failed safely on QA and Cloud restored0.1.3;0.2.1 fixes this exact failure.

The native setup asset loader requires a plain `.js` hook path and supplies its own asset version. Do not append a query-string version in `setup_wizard_requires`;0.2.1 passed migration but this loader rejected its versioned path.0.2.2 corrects the hook contract.
