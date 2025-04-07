# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate

def on_company_update(doc, method=None):
    """
    Handle company updates
    
    Args:
        doc: Company document
        method: Method name
    """
    # Validate Lebanese-specific fields
    validate_lebanese_company_settings(doc)
    
    # Create default NSSF components if they don't exist
    create_default_nssf_components(doc)
    
    # Set up default accounts if needed
    setup_default_accounts(doc)

def validate_lebanese_company_settings(company):
    """
    Validate Lebanese-specific company settings
    
    Args:
        company: Company document
    """
    # Check if LBP currency symbol is set
    if not company.get("lbp_currency_symbol"):
        company.lbp_currency_symbol = "ل.ل"
        frappe.msgprint(_("LBP Currency Symbol set to default (ل.ل)"), alert=True)
    
    # Check if NSSF rates are set
    if not company.get("nssf_employer_rate"):
        company.nssf_employer_rate = 21.5
        frappe.msgprint(_("NSSF Employer Rate set to default (21.5%)"), alert=True)
    
    if not company.get("nssf_employee_rate"):
        company.nssf_employee_rate = 2.0
        frappe.msgprint(_("NSSF Employee Rate set to default (2.0%)"), alert=True)
    
    # Check if required accounts are set
    if not company.get("indemnity_accrual_account"):
        frappe.msgprint(_("Indemnity Accrual Account not set. Please set it up for proper indemnity tracking."), 
                       alert=True, indicator="orange")
    
    if not company.get("nssf_payable_account"):
        frappe.msgprint(_("NSSF Payable Account not set. Please set it up for proper NSSF tracking."), 
                       alert=True, indicator="orange")

def create_default_nssf_components(company):
    """
    Create default NSSF salary components if they don't exist
    
    Args:
        company: Company document
    """
    # Check if NSSF Employee Contribution component exists
    employee_component = frappe.db.exists("Salary Component", "NSSF Employee Contribution")
    
    if not employee_component:
        # Create NSSF Employee Contribution component
        component = frappe.new_doc("Salary Component")
        component.salary_component = "NSSF Employee Contribution"
        component.salary_component_abbr = "NSSF-E"
        component.type = "Deduction"
        component.is_tax_applicable = 0
        component.variable_based_on_taxable_salary = 0
        component.is_nssf_deduction = 1
        component.description = _("National Social Security Fund - Employee Contribution")
        
        # Add company in accounts table
        component.append("accounts", {
            "company": company.name,
            "default_account": company.get("nssf_payable_account")
        })
        
        component.insert()
        
        frappe.msgprint(_("Created NSSF Employee Contribution salary component"), alert=True)
    
    # Check if NSSF Employer Contribution component exists
    employer_component = frappe.db.exists("Salary Component", "NSSF Employer Contribution")
    
    if not employer_component:
        # Create NSSF Employer Contribution component
        component = frappe.new_doc("Salary Component")
        component.salary_component = "NSSF Employer Contribution"
        component.salary_component_abbr = "NSSF-ER"
        component.type = "Earning"
        component.is_tax_applicable = 0
        component.do_not_include_in_total = 1
        component.is_nssf_employer_contribution = 1
        component.description = _("National Social Security Fund - Employer Contribution")
        
        # Add company in accounts table
        component.append("accounts", {
            "company": company.name,
            "default_account": company.get("nssf_payable_account")
        })
        
        component.insert()
        
        frappe.msgprint(_("Created NSSF Employer Contribution salary component"), alert=True)
    
    # Check if End of Service Indemnity component exists
    indemnity_component = frappe.db.exists("Salary Component", "End of Service Indemnity")
    
    if not indemnity_component:
        # Create End of Service Indemnity component
        component = frappe.new_doc("Salary Component")
        component.salary_component = "End of Service Indemnity"
        component.salary_component_abbr = "EoSI"
        component.type = "Earning"
        component.is_tax_applicable = 0
        component.do_not_include_in_total = 1
        component.is_indemnity_contribution = 1
        component.description = _("End of Service Indemnity Accrual")
        
        # Add company in accounts table
        component.append("accounts", {
            "company": company.name,
            "default_account": company.get("indemnity_accrual_account")
        })
        
        component.insert()
        
        frappe.msgprint(_("Created End of Service Indemnity salary component"), alert=True)

def setup_default_accounts(company):
    """
    Set up default accounts for Lebanese-specific features if they don't exist
    
    Args:
        company: Company document
    """
    # Check if chart of accounts exists
    if not frappe.db.exists("Account", {"company": company.name, "is_group": 1, "parent_account": ""}):
        frappe.msgprint(_("Chart of Accounts not set up for company {0}. Please set up the Chart of Accounts first.").format(company.name),
                       alert=True, indicator="red")
        return
    
    # Create NSSF Payable Account if it doesn't exist and not set
    if not company.get("nssf_payable_account"):
        # Check if account already exists
        nssf_account = frappe.db.exists("Account", {
            "company": company.name,
            "account_name": "NSSF Payable"
        })
        
        if nssf_account:
            company.nssf_payable_account = nssf_account
            frappe.msgprint(_("NSSF Payable Account set to existing account: {0}").format(nssf_account), alert=True)
        else:
            # Find Duties and Taxes parent account
            duties_account = frappe.db.exists("Account", {
                "company": company.name,
                "account_name": "Duties and Taxes",
                "is_group": 1
            })
            
            if duties_account:
                # Create NSSF Payable account
                account = frappe.new_doc("Account")
                account.account_name = "NSSF Payable"
                account.company = company.name
                account.parent_account = duties_account
                account.account_type = "Tax"
                account.account_currency = "LBP"
                account.insert()
                
                company.nssf_payable_account = account.name
                frappe.msgprint(_("Created NSSF Payable Account: {0}").format(account.name), alert=True)
    
    # Create Indemnity Accrual Account if it doesn't exist and not set
    if not company.get("indemnity_accrual_account"):
        # Check if account already exists
        indemnity_account = frappe.db.exists("Account", {
            "company": company.name,
            "account_name": "End of Service Indemnity"
        })
        
        if indemnity_account:
            company.indemnity_accrual_account = indemnity_account
            frappe.msgprint(_("Indemnity Accrual Account set to existing account: {0}").format(indemnity_account), alert=True)
        else:
            # Find Provisions parent account
            provisions_account = frappe.db.exists("Account", {
                "company": company.name,
                "account_name": "Provisions",
                "is_group": 1
            })
            
            if provisions_account:
                # Create Indemnity Accrual account
                account = frappe.new_doc("Account")
                account.account_name = "End of Service Indemnity"
                account.company = company.name
                account.parent_account = provisions_account
                account.account_type = "Liability"
                account.account_currency = "LBP"
                account.insert()
                
                company.indemnity_accrual_account = account.name
                frappe.msgprint(_("Created Indemnity Accrual Account: {0}").format(account.name), alert=True)
    
    # Save company if changes were made
    if company.has_value_changed("nssf_payable_account") or company.has_value_changed("indemnity_accrual_account"):
        company.save()