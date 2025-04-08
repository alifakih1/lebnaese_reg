# Lebanese Regulations

Adapt ERPNext for Lebanese compliance with multi-currency financial reports, NSSF integration, and localization features.

## Features

### Localization & Base Setup

- Bilingual Arabic/English labels for all reports, forms, and print templates
- Default date format: DD/MM/YYYY (Lebanese standard)
- LBP symbol (ل.ل) support in all currency fields
- Multi-Currency Support using ERPNext's Currency Exchange doctype

### Payroll Compliance (via Frappe HRMS)

- NSSF Contributions:
  - Custom Salary Components for employee NSSF deduction and employer NSSF liability
  - Auto-calculate contributions using HRMS Payroll Entry
- End-of-Service Indemnity:
  - Extended Employee doctype with custom field for indemnity accrual rate
  - Custom report for indemnity computation during employee separation
- Income Tax:
  - Lebanese income tax slabs as HRMS Tax Slabs linked to Salary Structures

### Multi-Currency Financial Reports

- Modified reports to display:
  - Foreign currency amount (e.g., USD)
  - Exchange rate (from transaction date)
  - Converted LBP amount
- Updated reports:
  - General Ledger: Added columns for foreign currency and LBP amounts
  - Trial Balance: Shows totals in both currencies per account
  - Balance Sheet & P&L: Aggregates values in LBP with foreign currency breakdowns
  - Toggle Option: Show/hide foreign currency columns via report filters

### Compliance & Audit

- Lebanese GAAP Reports:
  - Balance Sheet and Profit & Loss statements with Lebanese account groupings
- Audit Checklist:
  - Custom doctype to track Lebanese audit requirements
- Deadline Alerts:
  - Uses ERPNext's Notification System for payroll deadlines

## Installation

### Prerequisites

- ERPNext v15
- Frappe HRMS

### Steps

1. Install the app:

```
bench get-app https://github.com/alifakih1/lebanese_regulations
bench --site your-site install-app lebanese_regulations --skip-assets
```

Note: The `--skip-assets` flag is important as it skips the asset building process, which may cause errors in some environments.

2. Import Lebanese Chart of Accounts:

```
bench --site your-site import-chart-of-accounts lebanese_regulations/setup/coa_leb.csv
```

3. Set up NSSF components:

```
bench --site your-site execute lebanese_regulations.install.after_install
```

### Manual Asset Building (Optional)

If you want to enable the frontend features of the app, you'll need to build the assets manually:

1. Navigate to the app directory:

```
cd /path/to/frappe-bench/apps/lebanese_regulations
```

2. Install the Node.js dependencies:

```
npm install
```

3. Build the assets:

```
npm run build
```

4. Restart the bench:

```
bench restart
```

## Configuration

### Company Setup

1. Set LBP as the default currency for your company
2. Configure NSSF rates in Company settings
3. Set up indemnity accrual accounts

### Payroll Setup

1. Configure Salary Structures with NSSF components
2. Set up Income Tax Slabs according to Lebanese tax brackets
3. Configure Employee records with NSSF numbers and indemnity settings

## License

MIT
