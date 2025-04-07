# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint

def before_uninstall():
    """
    Run before uninstalling the app
    """
    # Check if there are any documents that would be affected
    check_existing_documents()
    
    # Remove custom fields
    remove_custom_fields()
    
    # Remove custom roles
    remove_custom_roles()
    
    # Clean up translations
    clean_up_translations()

def after_uninstall():
    """
    Run after uninstalling the app
    """
    # Send notification to administrators
    send_uninstall_notification()

def check_existing_documents():
    """
    Check if there are any documents that would be affected by uninstallation
    """
    # Check for Lebanese Audit Checklists
    audit_checklists = frappe.db.count("Lebanese Audit Checklist")
    
    if audit_checklists > 0:
        frappe.msgprint(
            _("There are {0} Lebanese Audit Checklists that will be deleted during uninstallation.").format(audit_checklists),
            alert=True, indicator="red"
        )
    
    # Check for NSSF components
    nssf_components = frappe.db.count(
        "Salary Component",
        {
            "name": ["in", ["NSSF Employee Contribution", "NSSF Employer Contribution", "End of Service Indemnity"]]
        }
    )
    
    if nssf_components > 0:
        frappe.msgprint(
            _("There are {0} NSSF Salary Components that will be affected during uninstallation.").format(nssf_components),
            alert=True, indicator="orange"
        )
    
    # Check for employees with NSSF data
    employees_with_nssf = frappe.db.count(
        "Employee",
        {
            "nssf_number": ["not in", ["", None]]
        }
    )
    
    if employees_with_nssf > 0:
        frappe.msgprint(
            _("There are {0} Employees with NSSF data that will be affected during uninstallation.").format(employees_with_nssf),
            alert=True, indicator="orange"
        )
    
    # Check for indemnity accruals
    employees_with_indemnity = frappe.db.count(
        "Employee",
        {
            "indemnity_accrual_amount": [">", 0]
        }
    )
    
    if employees_with_indemnity > 0:
        frappe.msgprint(
            _("There are {0} Employees with indemnity accruals that will be affected during uninstallation.").format(employees_with_indemnity),
            alert=True, indicator="orange"
        )

def remove_custom_fields():
    """
    Remove custom fields created by the app
    """
    # Get all custom fields created by the app
    custom_fields = frappe.get_all(
        "Custom Field",
        filters={
            "name": ["in", (
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
            )]
        },
        pluck="name"
    )
    
    # Delete custom fields
    for field in custom_fields:
        try:
            frappe.delete_doc("Custom Field", field)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Error deleting custom field {field}: {str(e)}", "Uninstall Lebanese Regulations")
    
    frappe.msgprint(_("Removed {0} custom fields").format(len(custom_fields)))

def remove_custom_roles():
    """
    Remove custom roles created by the app
    """
    # Get all custom roles created by the app
    custom_roles = frappe.get_all(
        "Role",
        filters={
            "name": ["in", ("Compliance Manager", "Payroll Officer")],
            "is_custom": 1
        },
        pluck="name"
    )
    
    # Delete custom roles
    for role in custom_roles:
        try:
            frappe.delete_doc("Role", role)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Error deleting custom role {role}: {str(e)}", "Uninstall Lebanese Regulations")
    
    frappe.msgprint(_("Removed {0} custom roles").format(len(custom_roles)))

def clean_up_translations():
    """
    Clean up translations created by the app
    """
    # Delete translations
    frappe.db.sql("""
        DELETE FROM `tabTranslation`
        WHERE source_name LIKE '%Lebanese%'
    """)
    
    frappe.db.commit()
    
    frappe.msgprint(_("Cleaned up translations"))

def send_uninstall_notification():
    """
    Send notification to administrators about uninstallation
    """
    # Get system managers
    system_managers = frappe.db.sql_list("""
        SELECT DISTINCT u.email
        FROM `tabUser` u
        JOIN `tabHas Role` r ON r.parent = u.name
        WHERE r.role = 'System Manager'
          AND u.enabled = 1
          AND u.email IS NOT NULL
          AND u.email != ''
    """)
    
    if not system_managers:
        return
    
    # Create notification
    subject = _("Lebanese Regulations Module Uninstalled")
    
    message = _("The Lebanese Regulations module has been uninstalled from your ERPNext instance.")
    message += "<br><br>"
    message += _("Please note that:")
    message += "<ul>"
    message += f"<li>{_('All Lebanese Audit Checklists have been deleted')}</li>"
    message += f"<li>{_('Custom fields for NSSF and indemnity tracking have been removed')}</li>"
    message += f"<li>{_('Custom roles (Compliance Manager, Payroll Officer) have been removed')}</li>"
    message += "</ul>"
    message += "<br>"
    message += _("If you need to reinstall the module, you can do so using the Bench CLI.")
    
    # Send notification
    frappe.sendmail(
        recipients=system_managers,
        subject=subject,
        message=message
    )