# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, add_days, add_months, get_first_day, get_last_day

def get_notification_config():
    """
    Get notification configuration for Lebanese Regulations
    
    Returns:
        dict: Notification configuration
    """
    return {
        "for_doctype": {
            "Lebanese Audit Checklist": {"status": "Open"},
            "Salary Slip": {"docstatus": 0},
            "Payroll Entry": {"docstatus": 0},
            "Currency Exchange": {"docstatus": 0},
        },
        "for_module_doctypes": {
            "Lebanese Regulations": [
                "Lebanese Audit Checklist",
                "Lebanese Audit Checklist Item"
            ],
            "Payroll": [
                "Salary Slip",
                "Payroll Entry",
                "Salary Structure",
                "Salary Component"
            ],
            "Accounting": [
                "Currency Exchange",
                "Journal Entry",
                "Payment Entry"
            ]
        },
        "for_module": {
            "Lebanese Regulations": get_lebanese_regulations_notifications(),
            "Payroll": get_lebanese_payroll_notifications(),
            "Accounting": get_lebanese_accounting_notifications()
        }
    }

def get_lebanese_regulations_notifications():
    """
    Get Lebanese Regulations module notifications
    
    Returns:
        dict: Notification counts
    """
    notifications = {}
    
    # Count open audit checklists
    notifications["open_audit_checklists"] = frappe.db.count(
        "Lebanese Audit Checklist",
        {"status": "Open"}
    )
    
    # Count pending audit checklist items
    notifications["pending_audit_items"] = frappe.db.count(
        "Lebanese Audit Checklist Item",
        {"status": ["in", ["Pending", "In Progress"]]}
    )
    
    # Check for upcoming NSSF deadlines
    today = getdate()
    nssf_deadline = get_first_day(add_months(today, 0))
    nssf_deadline = add_days(nssf_deadline, 14)  # 15th of the month
    
    if today <= nssf_deadline and today >= add_days(nssf_deadline, -5):
        notifications["nssf_deadline_approaching"] = 1
    
    return notifications

def get_lebanese_payroll_notifications():
    """
    Get Lebanese payroll notifications
    
    Returns:
        dict: Notification counts
    """
    notifications = {}
    
    # Count employees without NSSF numbers
    notifications["employees_without_nssf"] = frappe.db.count(
        "Employee",
        {
            "status": "Active",
            "nssf_number": ["in", ["", None]]
        }
    )
    
    # Count employees without indemnity settings
    notifications["employees_without_indemnity"] = frappe.db.count(
        "Employee",
        {
            "status": "Active",
            "indemnity_accrual_rate": ["in", [0, "", None]]
        }
    )
    
    # Check for unprocessed payroll for previous month
    today = getdate()
    prev_month_end = add_days(get_first_day(today), -1)
    prev_month_start = get_first_day(prev_month_end)
    
    # Get all companies
    companies = frappe.get_all("Company", pluck="name")
    
    unprocessed_companies = 0
    
    for company in companies:
        # Check if payroll entries exist for the previous month
        payroll_entries = frappe.get_all(
            "Payroll Entry",
            filters={
                "company": company,
                "docstatus": 1,
                "start_date": [">=", prev_month_start],
                "end_date": ["<=", prev_month_end]
            },
            limit=1
        )
        
        if not payroll_entries:
            unprocessed_companies += 1
    
    if unprocessed_companies > 0:
        notifications["unprocessed_payroll"] = unprocessed_companies
    
    return notifications

def get_lebanese_accounting_notifications():
    """
    Get Lebanese accounting notifications
    
    Returns:
        dict: Notification counts
    """
    notifications = {}
    
    # Count outdated currency exchange rates (older than 7 days)
    today = getdate()
    week_ago = add_days(today, -7)
    
    outdated_rates = frappe.db.count(
        "Currency Exchange",
        {
            "to_currency": "LBP",
            "date": ["<", week_ago]
        }
    )
    
    if outdated_rates > 0:
        notifications["outdated_exchange_rates"] = outdated_rates
    
    # Count GL entries without foreign currency info
    missing_currency_info = frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabGL Entry`
        WHERE account_currency != 'LBP'
          AND (foreign_currency_amount IS NULL OR foreign_currency_amount = 0)
          AND docstatus = 1
    """)[0][0]
    
    if missing_currency_info > 0:
        notifications["missing_currency_info"] = missing_currency_info
    
    return notifications