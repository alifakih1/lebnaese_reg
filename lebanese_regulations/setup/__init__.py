# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def setup_company_defaults(doc, method=None):
    """
    Setup default settings for a company
    """
    # Set default accounts for Lebanese regulations
    if not doc.nssf_payable_account:
        create_nssf_account(doc)
    
    if not doc.indemnity_accrual_account:
        create_indemnity_account(doc)

def create_nssf_account(company):
    """
    Create NSSF Payable Account
    """
    if frappe.db.exists("Company", company.name):
        parent_account = frappe.db.get_value("Account", 
            {"company": company.name, "account_name": "Duties and Taxes", "is_group": 1})
        
        if not parent_account:
            parent_account = frappe.db.get_value("Account", 
                {"company": company.name, "account_name": "Tax Assets", "is_group": 1})
        
        if not parent_account:
            parent_account = frappe.db.get_value("Account", 
                {"company": company.name, "account_type": "Payable", "is_group": 1})
        
        if parent_account:
            nssf_account = frappe.get_doc({
                "doctype": "Account",
                "account_name": "NSSF Payable",
                "parent_account": parent_account,
                "company": company.name,
                "account_type": "Payable",
                "account_currency": company.default_currency,
                "is_group": 0
            })
            nssf_account.insert(ignore_if_duplicate=True)
            
            # Update company
            frappe.db.set_value("Company", company.name, "nssf_payable_account", nssf_account.name)

def create_indemnity_account(company):
    """
    Create Indemnity Accrual Account
    """
    if frappe.db.exists("Company", company.name):
        parent_account = frappe.db.get_value("Account", 
            {"company": company.name, "account_name": "Duties and Taxes", "is_group": 1})
        
        if not parent_account:
            parent_account = frappe.db.get_value("Account", 
                {"company": company.name, "account_name": "Liabilities", "is_group": 1})
        
        if parent_account:
            indemnity_account = frappe.get_doc({
                "doctype": "Account",
                "account_name": "End of Service Indemnity",
                "parent_account": parent_account,
                "company": company.name,
                "account_type": "Payable",
                "account_currency": company.default_currency,
                "is_group": 0
            })
            indemnity_account.insert(ignore_if_duplicate=True)
            
            # Update company
            frappe.db.set_value("Company", company.name, "indemnity_accrual_account", indemnity_account.name)

def setup_migrate():
    """
    Run after migration
    """
    # Update all companies with default settings
    companies = frappe.get_all("Company")
    for company in companies:
        doc = frappe.get_doc("Company", company.name)
        setup_company_defaults(doc)

def setup_wizard_complete(args=None):
    """
    Run after setup wizard is complete
    """
    # Verify Lebanese Chart of Accounts exists in the setup directory
    import os
    import shutil
    from frappe.utils import get_bench_path
    
    # Try multiple possible locations for the source file
    possible_source_paths = [
        os.path.join(get_bench_path(), "apps", "coa_leb.csv"),
        os.path.join(get_bench_path(), "apps", "lebanese_regulations", "coa_leb.csv"),
        os.path.join(get_bench_path(), "coa_leb.csv")
    ]
    
    target_path = os.path.join(get_bench_path(), "apps", "lebanese_regulations", "lebanese_regulations", "setup", "data", "coa_leb.csv")
    
    # Check if target directory exists, create if not
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    # Try to find and copy the file from any of the possible locations
    for source_path in possible_source_paths:
        if os.path.exists(source_path) and not os.path.exists(target_path):
            try:
                shutil.copy(source_path, target_path)
                frappe.msgprint(_("Lebanese Chart of Accounts copied to module directory"), alert=True)
                break
            except Exception as e:
                frappe.log_error(f"Error copying Lebanese Chart of Accounts: {str(e)}", "Setup Wizard")