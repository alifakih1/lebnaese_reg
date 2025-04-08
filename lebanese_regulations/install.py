# -*- coding: utf-8 -*-
# Copyright (c) 2023, Ali H. Fakih and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import os
import json

def before_install():
    """
    Setup for Lebanese Regulations module before installation
    """
    # Check if required apps are installed
    required_apps = ["erpnext", "hrms"]
    for app in required_apps:
        if not frappe.db.exists("Module Def", {"app_name": app}):
            frappe.throw(_("Please install {0} app before installing Lebanese Regulations").format(app))
    
    frappe.msgprint(_("Preparing to install Lebanese Regulations module..."))

def after_install():
    """
    Setup for Lebanese Regulations module after installation
    """
    # Create custom fields
    create_custom_fields()
    
    # Import Lebanese Chart of Accounts
    import_chart_of_accounts()
    
    # Create default salary components for NSSF
    create_salary_components()
    
    # Create roles
    create_roles()
    
    # Create notification for NSSF deadlines
    create_notifications()
    
    frappe.msgprint(_("Lebanese Regulations module has been installed successfully."))

def create_custom_fields():
    """
    Create custom fields for Lebanese Regulations
    """
    # Custom fields are defined in hooks.py fixtures
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    from lebanese_regulations.setup.custom_fields import get_custom_fields
    
    custom_fields = get_custom_fields()
    create_custom_fields(custom_fields)

def import_chart_of_accounts():
    """
    Import Lebanese Chart of Accounts
    """
    # Check if the COA file exists
    coa_path = frappe.get_app_path("lebanese_regulations", "setup", "data", "coa_leb.csv")
    
    if not os.path.exists(coa_path):
        # Try to find the file in other locations
        alternate_paths = [
            os.path.join(frappe.get_app_path("lebanese_regulations"), "coa_leb.csv"),
            os.path.join(frappe.get_app_path("erpnext"), "coa_leb.csv"),
            os.path.join(frappe.utils.get_bench_path(), "apps", "coa_leb.csv")
        ]
        
        for path in alternate_paths:
            if os.path.exists(path):
                coa_path = path
                break
    
    if not os.path.exists(coa_path):
        # Log error
        frappe.log_error(f"Lebanese Chart of Accounts file not found at {coa_path}", "Lebanese Regulations")
        frappe.msgprint(f"Lebanese Chart of Accounts file not found. Please check the installation.", alert=True)
        return
    
    # Import the chart of accounts
    try:
        from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import create_charts
        
        # Get all companies
        companies = frappe.get_all("Company", filters={"country": "Lebanon"})
        
        if not companies:
            frappe.msgprint(_("No Lebanese companies found. Chart of Accounts will not be imported."), alert=True)
            return
        
        for company in companies:
            # Check if company already has accounts
            if frappe.db.count("Account", {"company": company.name}) > 1:
                continue  # Skip if company already has accounts
                
            frappe.msgprint(_("Importing Lebanese Chart of Accounts for {0}").format(company.name))
            company_doc = frappe.get_doc("Company", company.name)
            
            create_charts(company_doc.name, "Lebanese Chart of Accounts", coa_path)
            
            frappe.msgprint(_("Lebanese Chart of Accounts imported successfully for {0}").format(company.name))
            
    except Exception as e:
        frappe.log_error(f"Error importing Lebanese Chart of Accounts: {str(e)}", "Lebanese Regulations")
        frappe.msgprint(_("Error importing Lebanese Chart of Accounts: {0}").format(str(e)), alert=True)

def create_salary_components():
    """
    Create default salary components for NSSF
    """
    components = [
        {
            "name": "NSSF Employee Contribution",
            "abbr": "NSSF-E",
            "type": "Deduction",
            "description": "Lebanese NSSF Employee Contribution",
            "is_nssf_deduction": 1
        },
        {
            "name": "NSSF Employer Contribution",
            "abbr": "NSSF-ER",
            "type": "Earning",
            "description": "Lebanese NSSF Employer Contribution",
            "is_nssf_employer_contribution": 1,
            "do_not_include_in_total": 1  # This is an accounting entry, not actual earnings
        },
        {
            "name": "End of Service Indemnity",
            "abbr": "EOSI",
            "type": "Earning",
            "description": "Lebanese End of Service Indemnity Accrual",
            "is_indemnity_contribution": 1,
            "do_not_include_in_total": 1  # This is an accounting entry, not actual earnings
        }
    ]
    
    for component in components:
        if not frappe.db.exists("Salary Component", component["name"]):
            doc = frappe.new_doc("Salary Component")
            doc.update(component)
            doc.insert()

def create_roles():
    """
    Create roles for Lebanese Regulations
    """
    roles = [
        {
            "name": "Compliance Manager",
            "desk_access": 1,
            "two_factor_auth": 0,
            "restrict_to_domain": "",
            "disabled": 0
        },
        {
            "name": "Payroll Officer",
            "desk_access": 1,
            "two_factor_auth": 0,
            "restrict_to_domain": "",
            "disabled": 0
        }
    ]
    
    for role in roles:
        if not frappe.db.exists("Role", role["name"]):
            doc = frappe.new_doc("Role")
            doc.update(role)
            doc.insert()

def create_notifications():
    """
    Create notifications for NSSF deadlines
    """
    if not frappe.db.exists("Notification", "NSSF Submission Deadline"):
        notification = frappe.new_doc("Notification")
        notification.name = "NSSF Submission Deadline"
        notification.subject = "NSSF Submission Deadline Approaching"
        notification.document_type = "Company"
        notification.event = "Days Before"
        notification.days_in_advance = 5
        notification.message = """Dear {{ doc.owner }},

This is a reminder that the NSSF submission deadline for {{ doc.company_name }} is approaching in 5 days.

Please ensure all payroll entries are processed and NSSF contributions are calculated correctly.

Regards,
ERPNext"""
        notification.insert()