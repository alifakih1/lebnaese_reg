# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, add_days, add_months, get_first_day, get_last_day

def send_nssf_deadline_reminders():
    """
    Send reminders for NSSF submission deadlines
    """
    # NSSF submissions are due by the 15th of the following month
    today = getdate()
    next_month = add_months(today, 1)
    deadline = getdate(f"{next_month.year}-{next_month.month}-15")
    
    # Calculate days until deadline
    days_until_deadline = (deadline - today).days
    
    # Send reminders if deadline is approaching (5, 3, and 1 day before)
    if days_until_deadline in [5, 3, 1]:
        send_nssf_reminder(days_until_deadline)

def send_nssf_reminder(days_remaining):
    """
    Send NSSF deadline reminder to Compliance Managers and Payroll Officers
    """
    # Get all active companies
    companies = frappe.get_all("Company", fields=["name", "company_name"])
    
    for company in companies:
        # Create a notification
        notification = frappe.new_doc("Notification Log")
        notification.subject = f"NSSF Submission Deadline in {days_remaining} days"
        notification.for_user = get_compliance_managers(company.name)
        notification.type = "Alert"
        notification.document_type = "Company"
        notification.document_name = company.name
        notification.email_content = f"""
Dear Compliance Manager,

This is a reminder that the NSSF submission deadline for {company.company_name} is in {days_remaining} days.

Please ensure all payroll entries are processed and NSSF contributions are calculated correctly.

Regards,
ERPNext
"""
        notification.insert(ignore_permissions=True)

def get_compliance_managers(company):
    """
    Get users with Compliance Manager role for a company
    """
    # Get all users with Compliance Manager role
    users = frappe.get_all(
        "Has Role",
        filters={"role": "Compliance Manager", "parenttype": "User"},
        fields=["parent"]
    )
    
    # Filter users by company
    company_users = []
    for user in users:
        user_doc = frappe.get_doc("User", user.parent)
        if user_doc.enabled and is_user_for_company(user.parent, company):
            company_users.append(user.parent)
    
    return company_users

def is_user_for_company(user, company):
    """
    Check if user is associated with the company
    """
    # Check if user has a Employee record for the company
    employee = frappe.db.exists("Employee", {"user_id": user, "company": company})
    if employee:
        return True
    
    # Check if user has permission for the company
    has_permission = frappe.db.exists(
        "User Permission",
        {"user": user, "allow": "Company", "for_value": company}
    )
    
    return True if has_permission else False

def create_audit_checklist(company, fiscal_year):
    """
    Create an audit checklist for a company and fiscal year
    """
    # Check if checklist already exists
    existing = frappe.db.exists(
        "Lebanese Audit Checklist",
        {"company": company, "fiscal_year": fiscal_year}
    )
    
    if existing:
        return frappe.get_doc("Lebanese Audit Checklist", existing)
    
    # Create new checklist
    checklist = frappe.new_doc("Lebanese Audit Checklist")
    checklist.company = company
    checklist.fiscal_year = fiscal_year
    
    # Add standard checklist items
    checklist_items = [
        {
            "item": "NSSF Compliance",
            "description": "Verify all NSSF contributions have been calculated and paid correctly",
            "priority": "High",
            "status": "Pending"
        },
        {
            "item": "End of Service Indemnity Accruals",
            "description": "Verify End of Service Indemnity accruals have been calculated correctly",
            "priority": "High",
            "status": "Pending"
        },
        {
            "item": "Multi-Currency Reconciliation",
            "description": "Reconcile foreign currency accounts and verify exchange rate calculations",
            "priority": "Medium",
            "status": "Pending"
        },
        {
            "item": "Lebanese GAAP Compliance",
            "description": "Verify financial statements comply with Lebanese GAAP",
            "priority": "High",
            "status": "Pending"
        },
        {
            "item": "Income Tax Calculation",
            "description": "Verify income tax calculations for all employees",
            "priority": "High",
            "status": "Pending"
        }
    ]
    
    for item in checklist_items:
        checklist.append("items", item)
    
    checklist.insert(ignore_permissions=True)
    return checklist

def get_audit_status(company, fiscal_year=None):
    """
    Get audit status for a company
    """
    if not fiscal_year:
        from frappe.utils.nestedset import get_fiscal_year
        fiscal_year = get_fiscal_year(getdate())[0]
    
    # Get checklist
    checklist = frappe.db.exists(
        "Lebanese Audit Checklist",
        {"company": company, "fiscal_year": fiscal_year}
    )
    
    if not checklist:
        return {
            "status": "Not Started",
            "completed_items": 0,
            "total_items": 0,
            "completion_percentage": 0
        }
    
    # Get checklist items
    items = frappe.get_all(
        "Lebanese Audit Checklist Item",
        filters={"parent": checklist},
        fields=["status"]
    )
    
    total_items = len(items)
    completed_items = len([item for item in items if item.status == "Completed"])
    
    return {
        "status": "Completed" if completed_items == total_items else "In Progress",
        "completed_items": completed_items,
        "total_items": total_items,
        "completion_percentage": (completed_items / total_items * 100) if total_items > 0 else 0
    }