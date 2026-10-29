# YousrERP branding

Uses the approved YousrERP product wordmark with BOT Solutions navy #182b43, blue #2387f7 and dark surface #131b27. Assets are outlined SVG, with a compact toolbar export and a small favicon. No external font, tracking or API request is introduced. DM Sans licence is retained beside the assets. Original application source authorship/licence is preserved.

The Frappe app identifier remains `yousr_saudilization`. Existing Saudi custom fields and bilingual print formats are unchanged. Their presence does not prove ZATCA compliance or connected tax submission.

Installation and migration update only empty values and this app's legacy/new asset paths. Tenant-selected images and a custom app name are preserved. Uninstall removes only owned paths/name rather than clearing unrelated tenant settings. No explicit database commit occurs in hooks. Back up Website Settings/Navbar Settings before deployment. Native roles, permission checks, routes and theme selection are retained.

## Deploy and rollback

Back up the exact test site first. Add this app/revision to its disposable bench and install on the selected test site only. Run migrate/build/clear-cache through the hosting provider. Verify login, toolbar, theme, RTL, document editing and print formats. A bench deploy can restart both disposable test sites; do not select a production bench.

For rollback, deploy the recorded previous revision and restore the backed-up branding fields if needed. Do not uninstall as a cosmetic rollback: fixtures and custom fields may be in use. No production site is included in the showcase task.

## Demo media

Use synthetic company/person/contact data only. Do not enable email, WhatsApp, payment or tax integrations. Record installed-module capabilities honestly; HR/payroll or other optional apps require actual installation and plan qualification. Preserve invoice QA drafts from the earlier billing acceptance. Capture Chrome at a consistent viewport with no private provider/admin tabs in frame; record useful end-to-end actions, not just mouse movement over an empty list.

Asset URLs carry the app version so installed-site upgrades do not retain an older Desk script/stylesheet in browser cache. Bump the app version whenever these assets change.
