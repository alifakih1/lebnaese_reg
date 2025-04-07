# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, date_diff, add_months, get_first_day, get_last_day

def calculate_nssf_contributions(salary_slip):
    """
    Calculate NSSF contributions for an employee
    
    Args:
        salary_slip: Salary Slip document
    """
    if not salary_slip.employee:
        return
    
    # Get employee details
    employee = frappe.get_doc("Employee", salary_slip.employee)
    company = frappe.get_doc("Company", salary_slip.company)
    
    # Get NSSF rates from company settings
    employee_nssf_rate = company.get("nssf_employee_rate", 2.0)
    employer_nssf_rate = company.get("nssf_employer_rate", 21.5)
    
    # Get salary components
    employee_nssf_component = frappe.db.get_value("Salary Component", {"name": "NSSF Employee Contribution"})
    employer_nssf_component = frappe.db.get_value("Salary Component", {"name": "NSSF Employer Contribution"})
    
    if not employee_nssf_component or not employer_nssf_component:
        frappe.msgprint(_("NSSF Salary Components not found. Please create them first."), alert=True)
        return
    
    # Calculate base salary for NSSF
    base_salary = get_base_salary_for_nssf(salary_slip)
    
    # Calculate NSSF contributions
    employee_contribution = flt(base_salary) * flt(employee_nssf_rate) / 100
    employer_contribution = flt(base_salary) * flt(employer_nssf_rate) / 100
    
    # Add employee contribution to deductions
    add_nssf_to_salary_slip(
        salary_slip, 
        employee_nssf_component, 
        employee_contribution, 
        "deduction"
    )
    
    # Add employer contribution to earnings (for accounting purposes)
    add_nssf_to_salary_slip(
        salary_slip, 
        employer_nssf_component, 
        employer_contribution, 
        "earning"
    )
    
    # Store NSSF details in salary slip
    salary_slip.nssf_employee_contribution = employee_contribution
    salary_slip.nssf_employer_contribution = employer_contribution
    salary_slip.total_nssf_contribution = employee_contribution + employer_contribution

def get_base_salary_for_nssf(salary_slip):
    """
    Get base salary for NSSF calculation
    
    Args:
        salary_slip: Salary Slip document
        
    Returns:
        float: Base salary for NSSF calculation
    """
    # In Lebanon, NSSF is calculated on basic salary plus fixed allowances
    # Get all earnings that should be included in NSSF calculation
    nssf_applicable_components = frappe.get_all(
        "Salary Component",
        filters={"is_nssf_applicable": 1},
        pluck="name"
    )
    
    base_salary = 0
    for earning in salary_slip.earnings:
        if earning.salary_component in nssf_applicable_components:
            base_salary += flt(earning.amount)
    
    # Apply NSSF ceiling if configured
    nssf_ceiling = frappe.db.get_single_value("HR Settings", "nssf_salary_ceiling") or 0
    if nssf_ceiling > 0 and base_salary > nssf_ceiling:
        base_salary = nssf_ceiling
    
    return base_salary

def add_nssf_to_salary_slip(salary_slip, component, amount, type_of_component):
    """
    Add NSSF component to salary slip
    
    Args:
        salary_slip: Salary Slip document
        component: Salary Component
        amount: Amount
        type_of_component: Type of component (earning or deduction)
    """
    # Check if component already exists
    component_row = None
    if type_of_component == "earning":
        for d in salary_slip.earnings:
            if d.salary_component == component:
                component_row = d
                break
    else:
        for d in salary_slip.deductions:
            if d.salary_component == component:
                component_row = d
                break
    
    # If component exists, update amount
    if component_row:
        component_row.amount = amount
    else:
        # Add new component
        component_dict = {
            "salary_component": component,
            "amount": amount,
            "default_amount": amount
        }
        
        if type_of_component == "earning":
            salary_slip.append("earnings", component_dict)
        else:
            salary_slip.append("deductions", component_dict)

def calculate_indemnity_accrual(employee, posting_date=None):
    """
    Calculate end of service indemnity accrual for an employee
    
    Args:
        employee: Employee document or ID
        posting_date: Posting date for accrual
        
    Returns:
        float: Indemnity accrual amount
    """
    if isinstance(employee, str):
        employee = frappe.get_doc("Employee", employee)
    
    if not posting_date:
        posting_date = getdate()
    
    # Get indemnity settings
    indemnity_rate = employee.get("indemnity_accrual_rate", 8.33)  # Default: 1 month per year (8.33%)
    indemnity_start_date = employee.get("indemnity_start_date") or employee.date_of_joining
    
    if not indemnity_start_date:
        return 0
    
    # Calculate service period in months
    service_months = (date_diff(posting_date, indemnity_start_date) / 30.0)
    
    # Get monthly salary
    monthly_salary = get_monthly_salary_for_indemnity(employee)
    
    # Calculate indemnity accrual
    indemnity_accrual = monthly_salary * (service_months / 12.0) * (indemnity_rate / 100.0)
    
    return indemnity_accrual

def get_monthly_salary_for_indemnity(employee):
    """
    Get monthly salary for indemnity calculation
    
    Args:
        employee: Employee document
        
    Returns:
        float: Monthly salary for indemnity calculation
    """
    # Get latest salary slip
    salary_slip = frappe.get_all(
        "Salary Slip",
        filters={
            "employee": employee.name,
            "docstatus": 1
        },
        fields=["base_gross_pay"],
        order_by="start_date desc",
        limit=1
    )
    
    if salary_slip:
        return flt(salary_slip[0].base_gross_pay)
    
    # If no salary slip, get salary from salary structure
    salary_structure_assignment = frappe.get_all(
        "Salary Structure Assignment",
        filters={
            "employee": employee.name,
            "docstatus": 1
        },
        fields=["base"],
        order_by="from_date desc",
        limit=1
    )
    
    if salary_structure_assignment:
        return flt(salary_structure_assignment[0].base)
    
    return 0

def create_nssf_payment_entry(company, posting_date, nssf_payable_account=None):
    """
    Create NSSF payment entry for a company
    
    Args:
        company: Company document or ID
        posting_date: Posting date for payment
        nssf_payable_account: NSSF payable account
        
    Returns:
        str: Payment Entry ID
    """
    if isinstance(company, str):
        company = frappe.get_doc("Company", company)
    
    # Get NSSF payable account
    if not nssf_payable_account:
        nssf_payable_account = company.get("nssf_payable_account")
    
    if not nssf_payable_account:
        frappe.throw(_("NSSF Payable Account not configured for company {0}").format(company.name))
    
    # Get month and year for NSSF payment
    month_start = get_first_day(posting_date)
    month_end = get_last_day(month_start)
    prev_month_start = get_first_day(add_months(month_start, -1))
    prev_month_end = get_last_day(prev_month_start)
    
    # Calculate total NSSF contributions for the previous month
    total_nssf = frappe.db.sql("""
        SELECT SUM(nssf_employee_contribution) as employee_contribution,
               SUM(nssf_employer_contribution) as employer_contribution
        FROM `tabSalary Slip`
        WHERE company = %s
          AND docstatus = 1
          AND start_date >= %s
          AND end_date <= %s
    """, (company.name, prev_month_start, prev_month_end), as_dict=1)
    
    if not total_nssf or not (total_nssf[0].employee_contribution or total_nssf[0].employer_contribution):
        frappe.msgprint(_("No NSSF contributions found for {0} {1}").format(
            prev_month_start.strftime("%B"), prev_month_start.year
        ))
        return
    
    employee_contribution = flt(total_nssf[0].employee_contribution)
    employer_contribution = flt(total_nssf[0].employer_contribution)
    total_contribution = employee_contribution + employer_contribution
    
    # Create payment entry
    payment_entry = frappe.new_doc("Payment Entry")
    payment_entry.payment_type = "Pay"
    payment_entry.company = company.name
    payment_entry.posting_date = posting_date
    payment_entry.paid_from = nssf_payable_account
    payment_entry.paid_amount = total_contribution
    payment_entry.reference_no = f"NSSF-{prev_month_start.strftime('%m-%Y')}"
    payment_entry.reference_date = posting_date
    payment_entry.party_type = "Supplier"
    payment_entry.party = "National Social Security Fund"  # This supplier should be created
    
    # Add custom fields
    payment_entry.nssf_month = prev_month_start.strftime("%B %Y")
    payment_entry.nssf_employee_contribution = employee_contribution
    payment_entry.nssf_employer_contribution = employer_contribution
    
    return payment_entry.name

def update_indemnity_accrual(doc, method=None):
    """
    Update indemnity accrual when salary slip is submitted
    
    Args:
        doc: Salary Slip document
        method: Method name
    """
    if not doc.employee:
        return
    
    # Get employee details
    employee = frappe.get_doc("Employee", doc.employee)
    
    # Calculate indemnity accrual
    indemnity_amount = doc.get("indemnity_accrual_amount", 0)
    
    if not indemnity_amount:
        return
    
    # Update employee indemnity accrual amount
    current_accrual = flt(employee.get("indemnity_accrual_amount", 0))
    employee.indemnity_accrual_amount = current_accrual + indemnity_amount
    employee.save()
    
    frappe.msgprint(_("Employee indemnity accrual updated by {0}").format(
        frappe.format_value(indemnity_amount, {"fieldtype": "Currency"})
    ))

def setup_employee_defaults(doc, method=None):
    """
    Set up default values for Lebanese-specific fields when an employee is created
    
    Args:
        doc: Employee document
        method: Method name
    """
    # Set default indemnity accrual rate if not set
    if not doc.get("indemnity_accrual_rate"):
        doc.indemnity_accrual_rate = 8.33  # Default: 1 month per year (8.33%)
    
    # Set default indemnity start date if not set
    if not doc.get("indemnity_start_date"):
        doc.indemnity_start_date = doc.date_of_joining
    
    # Initialize indemnity accrual amount
    if not doc.get("indemnity_accrual_amount"):
        doc.indemnity_accrual_amount = 0

def validate_employee(doc, method=None):
    """
    Validate Lebanese-specific fields for an employee
    
    Args:
        doc: Employee document
        method: Method name
    """
    # Validate NSSF number format if provided
    nssf_number = doc.get("nssf_number")
    if nssf_number:
        # Lebanese NSSF numbers are typically 12 digits
        if not (nssf_number.isdigit() and len(nssf_number) == 12):
            frappe.msgprint(_("NSSF Number should be 12 digits"), alert=True, indicator="orange")
    
    # Validate indemnity accrual rate
    indemnity_rate = flt(doc.get("indemnity_accrual_rate"))
    if indemnity_rate <= 0 or indemnity_rate > 100:
        frappe.msgprint(_("Indemnity Accrual Rate should be between 0 and 100"), alert=True, indicator="orange")
        doc.indemnity_accrual_rate = 8.33  # Reset to default

def update_monthly_indemnity_accrual():
    """
    Monthly scheduled task to update indemnity accruals for all employees
    """
    # Get all active employees
    employees = frappe.get_all(
        "Employee",
        filters={"status": "Active"},
        fields=["name", "company"]
    )
    
    if not employees:
        return
    
    # Get current date
    posting_date = getdate()
    
    # Process each employee
    for emp in employees:
        # Calculate indemnity accrual
        indemnity_amount = calculate_indemnity_accrual(emp.name, posting_date)
        
        if indemnity_amount <= 0:
            continue
        
        # Get employee
        employee = frappe.get_doc("Employee", emp.name)
        
        # Update employee indemnity accrual amount
        current_accrual = flt(employee.get("indemnity_accrual_amount", 0))
        employee.indemnity_accrual_amount = current_accrual + indemnity_amount
        employee.save()
        
        # Create journal entry for indemnity accrual
        create_indemnity_accrual_entry(employee, indemnity_amount, posting_date)
    
    frappe.msgprint(_("Monthly indemnity accrual updated for all employees"))

def create_indemnity_accrual_entry(employee, amount, posting_date):
    """
    Create journal entry for indemnity accrual
    
    Args:
        employee: Employee document
        amount: Indemnity accrual amount
        posting_date: Posting date
    """
    if not amount or amount <= 0:
        return
    
    # Get company details
    company = frappe.get_doc("Company", employee.company)
    indemnity_accrual_account = company.get("indemnity_accrual_account")
    
    if not indemnity_accrual_account:
        frappe.msgprint(_("Indemnity Accrual Account not configured for company {0}").format(company.name),
                       alert=True, indicator="orange")
        return
    
    # Create journal entry
    je = frappe.new_doc("Journal Entry")
    je.posting_date = posting_date
    je.company = company.name
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
        frappe.msgprint(_("Default Expense Account not found. Please set it up for company {0}").format(company.name),
                       alert=True, indicator="orange")
        return
        
    je.append("accounts", {
        "account": default_expense_account,
        "debit_in_account_currency": amount,
        "reference_type": "Employee",
        "reference_name": employee.name
    })
    
    # Add liability
    je.append("accounts", {
        "account": indemnity_accrual_account,
        "credit_in_account_currency": amount,
        "reference_type": "Employee",
        "reference_name": employee.name
    })
    
    je.insert()
    je.submit()