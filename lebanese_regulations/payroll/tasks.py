# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate, add_days, add_months, get_first_day, get_last_day

def send_nssf_submission_reminder():
    """
    Send NSSF submission reminder to users with Compliance Manager role
    This is scheduled to run on the 15th of each month
    """
    # Get current date
    today = getdate()
    
    # Get previous month's date range
    prev_month_end = add_days(get_first_day(today), -1)
    prev_month_start = get_first_day(prev_month_end)
    prev_month_name = prev_month_end.strftime("%B %Y")
    
    # Get all companies
    companies = frappe.get_all("Company", pluck="name")
    
    if not companies:
        return
    
    # Get users with Compliance Manager role
    users = get_users_with_role("Compliance Manager")
    
    if not users:
        # If no Compliance Manager, try Payroll Officer
        users = get_users_with_role("Payroll Officer")
        
        if not users:
            # If no Payroll Officer either, try HR Manager
            users = get_users_with_role("HR Manager")
            
            if not users:
                # If no HR Manager either, try System Manager
                users = get_users_with_role("System Manager")
    
    if not users:
        frappe.log_error("No users found to send NSSF submission reminder", "NSSF Reminder")
        return
    
    # Check if all companies have processed payroll for the previous month
    unprocessed_companies = []
    
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
            unprocessed_companies.append(company)
    
    # Create the message
    subject = _("NSSF Submission Reminder for {0}").format(prev_month_name)
    
    message = _("This is a reminder that the NSSF submission deadline for {0} is approaching.").format(prev_month_name)
    message += "<br><br>"
    
    if unprocessed_companies:
        message += _("The following companies have not processed payroll for {0}:").format(prev_month_name)
        message += "<ul>"
        for company in unprocessed_companies:
            message += f"<li>{company}</li>"
        message += "</ul>"
        message += _("Please process payroll for these companies as soon as possible.")
        message += "<br><br>"
    
    message += _("Steps to submit NSSF contributions:")
    message += "<ol>"
    message += f"<li>{_('Ensure all payroll entries for')} {prev_month_name} {_('are processed and submitted')}</li>"
    message += f"<li>{_('Generate the NSSF report from Lebanese Regulations > Reports > NSSF Contributions')}</li>"
    message += f"<li>{_('Create payment entry for NSSF contributions')}</li>"
    message += f"<li>{_('Submit the report and payment to the NSSF office')}</li>"
    message += "</ol>"
    
    message += _("The deadline for submission is the 15th of the current month.")
    
    # Send the reminder to all users
    for user in users:
        frappe.sendmail(
            recipients=user,
            subject=subject,
            message=message,
            reference_doctype="Company",
            reference_name=companies[0] if companies else "NSSF Reminder"
        )
    
    frappe.log_error(f"NSSF submission reminder sent to {len(users)} users", "NSSF Reminder")

def get_users_with_role(role):
    """
    Get all users with a specific role
    
    Args:
        role: Role name
        
    Returns:
        list: List of user emails
    """
    return frappe.db.sql_list("""
        SELECT DISTINCT u.email
        FROM `tabUser` u
        JOIN `tabHas Role` r ON r.parent = u.name
        WHERE r.role = %s
          AND u.enabled = 1
          AND u.email IS NOT NULL
          AND u.email != ''
    """, role)

def process_nssf_payments():
    """
    Process NSSF payments for all companies
    This can be scheduled to run on the 15th of each month
    """
    # Get current date
    today = getdate()
    
    # Get all companies
    companies = frappe.get_all("Company", pluck="name")
    
    if not companies:
        return
    
    # Process each company
    for company_name in companies:
        company = frappe.get_doc("Company", company_name)
        
        # Check if NSSF payable account is set
        nssf_payable_account = company.get("nssf_payable_account")
        
        if not nssf_payable_account:
            frappe.log_error(f"NSSF Payable Account not set for company {company_name}", "NSSF Payment Processing")
            continue
        
        # Create NSSF payment entry
        from lebanese_regulations.payroll.utils import create_nssf_payment_entry
        
        payment_entry = create_nssf_payment_entry(company, today, nssf_payable_account)
        
        if payment_entry:
            frappe.msgprint(_("Created NSSF payment entry {0} for company {1}").format(
                payment_entry, company_name
            ))

def process_indemnity_accruals():
    """
    Process end of service indemnity accruals for all employees
    This can be scheduled to run monthly
    """
    # Get current date
    today = getdate()
    
    # Get all active employees
    employees = frappe.get_all(
        "Employee",
        filters={"status": "Active"},
        fields=["name", "company"]
    )
    
    if not employees:
        return
    
    # Process each employee
    for emp in employees:
        # Calculate indemnity accrual
        from lebanese_regulations.payroll.utils import calculate_indemnity_accrual
        
        indemnity_amount = calculate_indemnity_accrual(emp.name, today)
        
        if indemnity_amount <= 0:
            continue
        
        # Get employee
        employee = frappe.get_doc("Employee", emp.name)
        
        # Update employee indemnity accrual amount
        current_accrual = flt(employee.get("indemnity_accrual_amount", 0))
        employee.indemnity_accrual_amount = current_accrual + indemnity_amount
        employee.save()
        
        # Create journal entry for indemnity accrual
        company = frappe.get_doc("Company", emp.company)
        indemnity_accrual_account = company.get("indemnity_accrual_account")
        
        if not indemnity_accrual_account:
            frappe.log_error(f"Indemnity Accrual Account not set for company {emp.company}", "Indemnity Accrual Processing")
            continue
        
        # Create journal entry
        je = frappe.new_doc("Journal Entry")
        je.posting_date = today
        je.company = emp.company
        je.user_remark = _("Monthly Indemnity Accrual for {0}").format(employee.employee_name)
        
        # Add expense
        # Get default expense account or fallback to a standard expense account
        default_expense_account = company.get("default_expense_account")
        if not default_expense_account:
            default_expense_account = frappe.db.get_value("Account",
                {"company": company.name, "account_name": "Salary", "is_group": 0})
        
        if not default_expense_account:
            default_expense_account = frappe.db.get_value("Account",
                {"company": company.name, "account_type": "Expense", "is_group": 0})
        
        if not default_expense_account:
            frappe.log_error(f"Default Expense Account not found for company {company.name}", "Indemnity Accrual Processing")
            continue
            
        je.append("accounts", {
            "account": default_expense_account,
            "debit_in_account_currency": indemnity_amount,
            "reference_type": "Employee",
            "reference_name": emp.name
        })
        
        # Add liability
        je.append("accounts", {
            "account": indemnity_accrual_account,
            "credit_in_account_currency": indemnity_amount,
            "reference_type": "Employee",
            "reference_name": emp.name
        })
        
        je.insert()
        je.submit()
        
        frappe.msgprint(_("Processed indemnity accrual for employee {0}").format(employee.employee_name))