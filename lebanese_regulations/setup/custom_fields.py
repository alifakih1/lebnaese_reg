# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def get_custom_fields():
    """
    Returns a dictionary of custom fields for Lebanese Regulations
    """
    custom_fields = {
        "Company": [
            {
                "fieldname": "lbp_currency_symbol",
                "label": "LBP Currency Symbol",
                "fieldtype": "Data",
                "insert_after": "default_currency",
                "default": "ل.ل",
                "description": "Symbol for Lebanese Pound (LBP)"
            },
            {
                "fieldname": "nssf_employer_rate",
                "label": "NSSF Employer Contribution Rate",
                "fieldtype": "Percent",
                "insert_after": "default_payroll_payable_account",
                "default": "21.5",
                "description": "Employer contribution rate for NSSF"
            },
            {
                "fieldname": "nssf_employee_rate",
                "label": "NSSF Employee Contribution Rate",
                "fieldtype": "Percent",
                "insert_after": "nssf_employer_rate",
                "default": "2",
                "description": "Employee contribution rate for NSSF"
            },
            {
                "fieldname": "indemnity_accrual_account",
                "label": "Indemnity Accrual Account",
                "fieldtype": "Link",
                "options": "Account",
                "insert_after": "nssf_employee_rate",
                "description": "Account for End of Service Indemnity accruals"
            },
            {
                "fieldname": "nssf_payable_account",
                "label": "NSSF Payable Account",
                "fieldtype": "Link",
                "options": "Account",
                "insert_after": "indemnity_accrual_account",
                "description": "Account for NSSF contributions payable"
            }
        ],
        "Employee": [
            {
                "fieldname": "nssf_number",
                "label": "NSSF Number",
                "fieldtype": "Data",
                "insert_after": "company_email",
                "description": "Lebanese National Social Security Fund Number"
            },
            {
                "fieldname": "indemnity_accrual_rate",
                "label": "Indemnity Accrual Rate",
                "fieldtype": "Percent",
                "insert_after": "nssf_number",
                "default": "8.33",
                "description": "Monthly accrual rate for End of Service Indemnity (default: 1 month per year = 8.33%)"
            },
            {
                "fieldname": "indemnity_accrual_amount",
                "label": "Indemnity Accrual Amount",
                "fieldtype": "Currency",
                "insert_after": "indemnity_accrual_rate",
                "read_only": 1,
                "description": "Total accrued End of Service Indemnity amount"
            },
            {
                "fieldname": "indemnity_start_date",
                "label": "Indemnity Start Date",
                "fieldtype": "Date",
                "insert_after": "indemnity_accrual_amount",
                "description": "Date from which to calculate End of Service Indemnity"
            }
        ],
        "Salary Component": [
            {
                "fieldname": "is_nssf_deduction",
                "label": "Is NSSF Employee Contribution",
                "fieldtype": "Check",
                "insert_after": "description",
                "description": "Check if this component is for NSSF employee contribution"
            },
            {
                "fieldname": "is_nssf_employer_contribution",
                "label": "Is NSSF Employer Contribution",
                "fieldtype": "Check",
                "insert_after": "is_nssf_deduction",
                "description": "Check if this component is for NSSF employer contribution"
            },
            {
                "fieldname": "is_indemnity_contribution",
                "label": "Is Indemnity Contribution",
                "fieldtype": "Check",
                "insert_after": "is_nssf_employer_contribution",
                "description": "Check if this component is for End of Service Indemnity accrual"
            }
        ],
        "GL Entry": [
            {
                "fieldname": "foreign_currency",
                "label": "Foreign Currency",
                "fieldtype": "Link",
                "options": "Currency",
                "insert_after": "account_currency",
                "description": "Foreign currency for this transaction"
            },
            {
                "fieldname": "foreign_currency_amount",
                "label": "Foreign Currency Amount",
                "fieldtype": "Currency",
                "insert_after": "foreign_currency",
                "description": "Amount in foreign currency"
            },
            {
                "fieldname": "exchange_rate",
                "label": "Exchange Rate",
                "fieldtype": "Float",
                "insert_after": "foreign_currency_amount",
                "precision": 6,
                "description": "Exchange rate between account currency and foreign currency"
            },
            {
                "fieldname": "lbp_amount",
                "label": "LBP Amount",
                "fieldtype": "Currency",
                "options": "LBP",
                "insert_after": "exchange_rate",
                "description": "Amount in LBP (Lebanese Pound)"
            }
        ],
        "Salary Slip": [
            {
                "fieldname": "nssf_number",
                "label": "NSSF Number",
                "fieldtype": "Data",
                "insert_after": "bank_account_no",
                "read_only": 1,
                "description": "Employee's NSSF Number"
            },
            {
                "fieldname": "nssf_employee_rate",
                "label": "NSSF Employee Rate",
                "fieldtype": "Percent",
                "insert_after": "nssf_number",
                "read_only": 1,
                "description": "NSSF Employee Contribution Rate"
            },
            {
                "fieldname": "nssf_employer_rate",
                "label": "NSSF Employer Rate",
                "fieldtype": "Percent",
                "insert_after": "nssf_employee_rate",
                "read_only": 1,
                "description": "NSSF Employer Contribution Rate"
            },
            {
                "fieldname": "nssf_employee_contribution",
                "label": "NSSF Employee Contribution",
                "fieldtype": "Currency",
                "insert_after": "nssf_employer_rate",
                "read_only": 1,
                "description": "NSSF Employee Contribution Amount"
            },
            {
                "fieldname": "nssf_employer_contribution",
                "label": "NSSF Employer Contribution",
                "fieldtype": "Currency",
                "insert_after": "nssf_employee_contribution",
                "read_only": 1,
                "description": "NSSF Employer Contribution Amount"
            },
            {
                "fieldname": "total_nssf_contribution",
                "label": "Total NSSF Contribution",
                "fieldtype": "Currency",
                "insert_after": "nssf_employer_contribution",
                "read_only": 1,
                "description": "Total NSSF Contribution Amount"
            },
            {
                "fieldname": "indemnity_accrual_rate",
                "label": "Indemnity Accrual Rate",
                "fieldtype": "Percent",
                "insert_after": "total_nssf_contribution",
                "read_only": 1,
                "description": "End of Service Indemnity Accrual Rate"
            },
            {
                "fieldname": "indemnity_accrual_amount",
                "label": "Indemnity Accrual Amount",
                "fieldtype": "Currency",
                "insert_after": "indemnity_accrual_rate",
                "read_only": 1,
                "description": "End of Service Indemnity Accrual Amount for this period"
            },
            {
                "fieldname": "nssf_employee_contribution_ytd",
                "label": "NSSF Employee Contribution YTD",
                "fieldtype": "Currency",
                "insert_after": "indemnity_accrual_amount",
                "read_only": 1,
                "description": "Year-to-date NSSF Employee Contribution"
            },
            {
                "fieldname": "nssf_employer_contribution_ytd",
                "label": "NSSF Employer Contribution YTD",
                "fieldtype": "Currency",
                "insert_after": "nssf_employee_contribution_ytd",
                "read_only": 1,
                "description": "Year-to-date NSSF Employer Contribution"
            },
            {
                "fieldname": "total_nssf_contribution_ytd",
                "label": "Total NSSF Contribution YTD",
                "fieldtype": "Currency",
                "insert_after": "nssf_employer_contribution_ytd",
                "read_only": 1,
                "description": "Year-to-date Total NSSF Contribution"
            },
            {
                "fieldname": "indemnity_accrual_amount_ytd",
                "label": "Indemnity Accrual Amount YTD",
                "fieldtype": "Currency",
                "insert_after": "total_nssf_contribution_ytd",
                "read_only": 1,
                "description": "Year-to-date End of Service Indemnity Accrual Amount"
            }
        ]
    }
    
    return custom_fields