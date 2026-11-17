# YousrERP workspace welcome

The app extends the supported version-16 setup hooks. It preserves native account, company, chart, fiscal-year and module validation and save handlers. Four native steps remain: preferences, workspace contact, working style, company. Users submit setup themselves. The extension creates no invoices, payments or tax submissions.

Portal login identity and workspace identity are separate. Authenticated server context may suggest the current subscription’s business name and a verified portal email. Every suggestion remains editable. A phone-only account receives no invented email. A personal portal email may be replaced with a business email in the native workspace profile. No change is copied back to portal login or billing identity. No passwords, OTPs or VAT records are transported. Context is hidden from guests and ordinary workspace staff.

The portal must explicitly enable context transfer; existing deployments default off. The site config is scoped to the exact customer workspace. Two subscriptions belonging to one owner retain different company suggestions. No global portal billing identity or industry is substituted for a workspace’s information.

For a newly unconfigured workspace, external diagnostics default off. Established tenant settings are preserved. The native Desk setup checklist is the only post-setup guide. The separate floating first-task card has been removed.

Source names, licence notices, app identifiers and backend routes remain intact. Customer presentation uses YousrERP branding; tenant-selected logos remain their own. Core Frappe/ERPNext files are not patched.

Rollback: restore the previous app revision/image using a verified Cloud backup; disable portal context transfer. Do not delete companies or rewrite confirmed workspace identities to undo presentation changes.

Migration acceptance: fresh System Settings has no language/time zone until native setup. Set only the telemetry boolean using the single-value database API; never save the incomplete settings document or invent required preferences. Version0.2.0 migration failed safely on QA and Cloud restored0.1.3;0.2.1 fixes this exact failure.

The native setup asset loader requires a plain `.js` hook path and supplies its own asset version. Do not append a query-string version in `setup_wizard_requires`;0.2.1 passed migration but this loader rejected its versioned path.0.2.2 corrects the hook contract.

Assets are loaded concurrently. The extension updates the native slide-settings objects as well as registered slides, preserving their handlers and making company suggestions independent of script arrival/registration order.

Owner suggestions are gated using the authoritative server `is_setup_complete()` check, independent of intermediate boot fields and hook order. Established workspaces never receive the owner profile just because a boot dictionary is incomplete.

## Managed product menus

The app adapts only native avatar dropdowns, using the original Dropdown component for keyboard/focus and retaining existing profile, theme, settings and logout callbacks. About is a branded product dialog; support and subscription billing open the owned portal in a separate tab. All other dropdowns remain untouched. V16 app-card metadata replaces only framework-default titles/icons while preserving native routes, permission flags and tenant custom branding.

Provider billing/Cloud-account login RPC shortcuts are denied through explicit supported whitelist overrides. Normal ERP accounting, setup, Cloud provisioning/SSO and operator-side Cloud access are not overridden. The frontend provider-settings button is hidden without changing `is_fc_site`, roles or site limits. Native billing proxy read-only denial probes are required in live QA; do not invoke charges, top-ups or plan changes as a test. Original source/licence notices remain intact.

## Optional practice data (0.3.0 candidate — QA required before rollout)

The last native company slide offers an unchecked EN/AR choice. A supported
`setup_wizard_success` hook queues work only after the real company setup
succeeds. It never replaces core setup handlers or runs demo seeding during
install/migration. Existing configured sites receive no new data automatically.
The `yousr_demo_enabled=false` site setting hides/disables new demo requests;
existing practice isolation guards remain active so disabling UI cannot mix data.

Practice data uses `Yousr Practice - DEMO`, prefix `YOUSR-DEMO-`, separate customer,
supplier/item groups and buying/selling price lists. The real company and global
company defaults must remain unchanged. Masters are site-global in ERPNext, so
we explicitly enforce both directions of the boundary on native document save:
DEMO links cannot enter real-company transactions; real masters cannot enter the
practice company. The records retain their DEMO identity and cannot be renamed
or merged. Draft quotations/purchase orders use explicit fictional values.
All practice-company submissions are blocked (no posted stock/accounting,
payments or ZATCA). Real documents retain native validation and submit behavior.
No invoices, legal identities, tax credentials, contacts, emails or messages
are seeded. This deliberately starts with draft exploration, not a copy of v15's
legacy generator or a functioning tax sandbox.

`Yousr Demo Setup` is a System-Manager-readable singleton with an exact owned
record manifest. The job uses a site-scoped lock and savepoint; failure rolls
back its practice changes and records a fixed error category, without undoing
native setup. Duplicate/retried setup does not reseed Ready data. Failed seeds
can retry only if no reserved company/partial manifest exists. Existing name
collisions fail closed; unrelated records are never adopted or overwritten.

The separate practice page labels all ZATCA response examples SIMULATED and
explains example acceptance/rejection and totals. It never modifies native
invoice tax status or claims actual clearance/reporting. Real sandbox tests
need a separately isolated test environment and scoped test credentials; never
use production CSIDs or submit these examples to a live endpoint.

Release gate: disposable Grow QA site; verify migration, optional on/off, real
company defaults, exact seeded records, failed/repeated job behavior, both-way
mixing rejection, invoice/payment/stock-submit rejection, tax credential refusal,
ordinary real-company drafts unaffected, EN/AR phone/laptop UI, and zero external
messages or tax requests. No live customer bench rollout before acceptance.
Rollback is previous app image plus pre-update backup; do not uninstall/drop the
state or isolation guards while practice records remain. No automatic deletion
or cleanup of customer-created records is included in this initial version.
