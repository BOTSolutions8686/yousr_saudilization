### YousrERP branding and Saudi fields

Yousr ERP Custom Application for custom branding, custom fields and customizations

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/BOTSolutions8686/yousr_saudilization.git --branch main
bench --site site_name install-app yousr_saudilization
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/yousr_saudilization
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade
### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit

Branding uses the YousrERP wordmark and BOT Solutions blue/navy identity, including native light/dark themes. Install/migrate updates only blank or app-owned logos; tenant logos are preserved. App identifier and existing Saudi fields/print-format names remain compatible. See `docs/BRANDING.md` for deployment and rollback.
