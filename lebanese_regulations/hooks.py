# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

app_name = "lebanese_regulations"
app_title = "Lebanese Regulations"
app_publisher = "Ali H. Fakih"
app_description = "Adapt ERPNext for Lebanese compliance"
app_icon = "octicon octicon-file-directory"
app_color = "#589494"
app_email = "info@kiwinmore.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/lebanese_regulations/css/lebanese_regulations.css"
# app_include_js = ["/assets/lebanese_regulations/dist/lebanese_regulations.bundle.js"]

# include js, css files in header of web template
# web_include_css = "/assets/lebanese_regulations/css/lebanese_regulations_web.css"
# web_include_js = "/assets/lebanese_regulations/js/lebanese_regulations_web.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "lebanese_regulations/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"Salary Slip": "/assets/lebanese_regulations/js/salary_slip.js"}
# webform_include_css = {"Salary Slip": "/assets/lebanese_regulations/css/salary_slip.css"}

# include js in page
# page_js = {"general-ledger" : "/assets/lebanese_regulations/js/general_ledger.js"}

# include js in doctype views
# doctype_js = {
#     "Company": "/assets/lebanese_regulations/js/company.js",
#     "Sales Invoice": "/assets/lebanese_regulations/js/sales_invoice.js",
#     "Purchase Invoice": "/assets/lebanese_regulations/js/purchase_invoice.js",
#     "Employee": "/assets/lebanese_regulations/js/employee.js",
#     "Salary Structure": "/assets/lebanese_regulations/js/salary_structure.js",
#     "Salary Slip": "/assets/lebanese_regulations/js/salary_slip.js",
#     "Payroll Entry": "/assets/lebanese_regulations/js/payroll_entry.js",
# }

# doctype_list_js = {
#     "Salary Slip": "/assets/lebanese_regulations/js/salary_slip_list.js",
#     "Currency Exchange": "/assets/lebanese_regulations/js/currency_exchange_list.js",
#     "Lebanese Audit Checklist": "/assets/lebanese_regulations/js/lebanese_audit_checklist_list.js"
# }
# doctype_tree_js = {"Account": "/assets/lebanese_regulations/js/account_tree.js"}
# doctype_calendar_js = {"Payroll Entry": "/assets/lebanese_regulations/js/payroll_entry_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
role_home_page = {
    "Compliance Manager": "lebanese-regulations",
    "Payroll Officer": "lebanese-regulations"
}

# Generators
# ----------

# automatically create page for each record of this doctype
website_generators = ["Lebanese Audit Checklist"]

# Installation
# ------------

before_install = "lebanese_regulations.install.before_install"
after_install = "lebanese_regulations.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

notification_config = "lebanese_regulations.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
    "Lebanese Audit Checklist": "lebanese_regulations.permissions.get_permission_query_conditions_for_audit_checklist",
}

has_permission = {
    "Lebanese Audit Checklist": "lebanese_regulations.permissions.has_permission_for_audit_checklist",
}

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
    "Salary Slip": "lebanese_regulations.overrides.salary_slip.LebaneseRegulationsSalarySlip",
    "Payroll Entry": "lebanese_regulations.overrides.payroll_entry.LebaneseRegulationsPayrollEntry"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Salary Slip": {
        "validate": "lebanese_regulations.payroll.utils.calculate_nssf_contributions",
        "on_submit": "lebanese_regulations.payroll.utils.update_indemnity_accrual",
    },
    "Employee": {
        "after_insert": "lebanese_regulations.payroll.utils.setup_employee_defaults",
        "validate": "lebanese_regulations.payroll.utils.validate_employee",
    },
    "Company": {
        "after_insert": "lebanese_regulations.setup.setup_company_defaults",
        "on_update": "lebanese_regulations.setup.events.on_company_update",
    },
    "GL Entry": {
        "validate": "lebanese_regulations.accounting.utils.add_currency_info",
    },
    "Currency Exchange": {
        "after_insert": "lebanese_regulations.accounting.events.on_currency_exchange_update",
        "on_update": "lebanese_regulations.accounting.events.on_currency_exchange_update",
    },
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "daily": [
        "lebanese_regulations.compliance.utils.send_nssf_deadline_reminders",
    ],
    "monthly": [
        "lebanese_regulations.payroll.utils.update_monthly_indemnity_accrual",
    ],
    "cron": {
        # Run on the 1st of every month at 00:00
        "0 0 1 * *": [
            "lebanese_regulations.accounting.tasks.process_month_end_exchange_rates"
        ],
        # Run on the 15th of every month at 09:00
        "0 9 15 * *": [
            "lebanese_regulations.payroll.tasks.send_nssf_submission_reminder"
        ]
    }
}

# Testing
# -------

before_tests = "lebanese_regulations.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
    "erpnext.accounts.report.general_ledger.general_ledger.get_result": "lebanese_regulations.report.lebanese_general_ledger.lebanese_general_ledger.get_result",
    "erpnext.payroll.doctype.salary_slip.salary_slip.make_salary_slip": "lebanese_regulations.payroll.overrides.make_salary_slip"
}

# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
override_doctype_dashboards = {
    "Salary Slip": "lebanese_regulations.payroll.dashboard.get_salary_slip_dashboard",
    "Company": "lebanese_regulations.setup.dashboard.get_company_dashboard"
}

# exempt linked doctypes from being automatically cancelled
auto_cancel_exempted_doctypes = ["Lebanese Audit Checklist"]

# Request Events
# --------------
before_request = ["lebanese_regulations.utils.before_request"]
after_request = ["lebanese_regulations.utils.after_request"]

# Job Events
# ----------
before_job = ["lebanese_regulations.utils.before_job"]
after_job = ["lebanese_regulations.utils.after_job"]

# User Data Protection
# --------------------

user_data_fields = [
    {
        "doctype": "Employee",
        "filter_by": "user_id",
        "redact_fields": ["nssf_number", "indemnity_accrual_rate", "indemnity_start_date"],
        "partial": 1,
    }
]

# Authentication and authorization
# --------------------------------

auth_hooks = [
    "lebanese_regulations.auth.validate"
]

# Translation
# -----------
# Make translations available in the frontend
translations = ["ar.csv"]

# Custom fields to be created
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                (
                    # Company fields
                    "Company-lbp_currency_symbol",
                    "Company-nssf_employer_rate",
                    "Company-nssf_employee_rate",
                    "Company-indemnity_accrual_account",
                    "Company-nssf_payable_account",
                    
                    # Employee fields
                    "Employee-nssf_number",
                    "Employee-indemnity_accrual_rate",
                    "Employee-indemnity_accrual_amount",
                    "Employee-indemnity_start_date",
                    
                    # Salary Component fields
                    "Salary Component-is_nssf_deduction",
                    "Salary Component-is_nssf_employer_contribution",
                    "Salary Component-is_indemnity_contribution",
                    
                    # GL Entry fields
                    "GL Entry-foreign_currency",
                    "GL Entry-foreign_currency_amount",
                    "GL Entry-exchange_rate",
                    
                    # Report fields
                    "GL Entry-lbp_amount",
                ),
            ],
        ],
    },
    {
        "dt": "Role",
        "filters": [
            [
                "name",
                "in",
                (
                    "Compliance Manager",
                    "Payroll Officer",
                ),
            ],
        ],
    },
]

# Regional Overrides
regional_overrides = {
    "Lebanon": {
        "erpnext.controllers.taxes_and_totals.update_itemised_tax_data": "lebanese_regulations.regional.lebanon.taxes.update_itemised_tax_data",
        "erpnext.accounts.utils.get_regional_address_details": "lebanese_regulations.regional.lebanon.taxes.get_regional_address_details",
        "erpnext.accounts.utils.get_regional_round_off_accounts": "lebanese_regulations.regional.lebanon.taxes.get_regional_round_off_accounts"
    },
}

# Jinja Environment
jinja = {
    "methods": [
        "lebanese_regulations.utils.jinja_methods.format_lbp_currency",
        "lebanese_regulations.utils.jinja_methods.format_arabic_date",
        "lebanese_regulations.utils.jinja_methods.format_bilingual_text",
        "lebanese_regulations.utils.jinja_methods.replace_english_with_arabic_numerals"
    ],
}