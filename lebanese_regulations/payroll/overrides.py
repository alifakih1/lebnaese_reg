# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate

@frappe.whitelist()
def make_salary_slip(source_name, target_doc=None, employee=None, as_print=False, print_format=None, for_preview=0):
    """
    Override standard make_salary_slip function to add Lebanese-specific customizations
    
    Args:
        source_name: Source document name
        target_doc: Target document
        employee: Employee ID
        as_print: Whether to return as print
        print_format: Print format
        for_preview: Whether for preview
        
    Returns:
        Salary Slip document
    """
    # Import the standard function
    from erpnext.payroll.doctype.salary_slip.salary_slip import make_salary_slip as standard_make_salary_slip
    
    # Use standard function to create the salary slip
    doc = standard_make_salary_slip(source_name, target_doc, employee, as_print, print_format, for_preview)
    
    # Add Lebanese-specific customizations
    if doc and doc.doctype == "Salary Slip":
        # Set Lebanese-specific fields
        company = frappe.get_doc("Company", doc.company)
        
        # Set NSSF rates from company settings
        doc.nssf_employee_rate = company.get("nssf_employee_rate", 2.0)
        doc.nssf_employer_rate = company.get("nssf_employer_rate", 21.5)
        
        # Get employee details
        if doc.employee:
            employee = frappe.get_doc("Employee", doc.employee)
            doc.nssf_number = employee.get("nssf_number", "")
            doc.indemnity_accrual_rate = employee.get("indemnity_accrual_rate", 8.33)
    
    return doc