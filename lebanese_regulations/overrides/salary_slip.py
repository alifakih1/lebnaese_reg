# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate
from erpnext.payroll.doctype.salary_slip.salary_slip import SalarySlip

class LebaneseRegulationsSalarySlip(SalarySlip):
    """
    Customized Salary Slip for Lebanese regulations
    """
    
    def validate(self):
        """
        Validate salary slip
        """
        # Run standard validation
        super(LebaneseRegulationsSalarySlip, self).validate()
        
        # Add Lebanese-specific validations
        self.validate_nssf_components()
        
    def validate_nssf_components(self):
        """
        Validate NSSF components
        """
        # Check if NSSF components are set up
        employee_nssf_component = frappe.db.get_value("Salary Component", {"is_nssf_deduction": 1})
        employer_nssf_component = frappe.db.get_value("Salary Component", {"is_nssf_employer_contribution": 1})
        
        if not employee_nssf_component or not employer_nssf_component:
            frappe.msgprint(_("NSSF Salary Components not properly set up. Please configure them in Salary Components."), 
                           alert=True, indicator="orange")
    
    def process_salary_structure(self):
        """
        Process salary structure
        """
        # Run standard processing
        super(LebaneseRegulationsSalarySlip, self).process_salary_structure()
        
        # Add Lebanese-specific processing
        self.calculate_nssf_contributions()
        self.calculate_indemnity_accrual()
    
    def calculate_nssf_contributions(self):
        """
        Calculate NSSF contributions
        """
        # This is a placeholder - the actual calculation is done in payroll.utils.calculate_nssf_contributions
        # which is called via hooks
        pass
    
    def calculate_indemnity_accrual(self):
        """
        Calculate end of service indemnity accrual
        """
        # Get indemnity component
        indemnity_component = frappe.db.get_value("Salary Component", {"is_indemnity_contribution": 1})
        
        if not indemnity_component:
            return
        
        # Get employee details
        employee = frappe.get_doc("Employee", self.employee)
        
        # Get indemnity settings
        indemnity_rate = employee.get("indemnity_accrual_rate", 8.33)  # Default: 1 month per year (8.33%)
        
        # Calculate indemnity accrual for this month
        monthly_salary = self.gross_pay
        monthly_accrual = flt(monthly_salary) * flt(indemnity_rate) / 100
        
        # Add indemnity component to earnings
        self.add_indemnity_to_salary_slip(indemnity_component, monthly_accrual)
        
        # Store indemnity details in salary slip
        self.indemnity_accrual_amount = monthly_accrual
    
    def add_indemnity_to_salary_slip(self, component, amount):
        """
        Add indemnity component to salary slip
        
        Args:
            component: Salary Component
            amount: Amount
        """
        # Check if component already exists
        component_row = None
        for d in self.earnings:
            if d.salary_component == component:
                component_row = d
                break
        
        # If component exists, update amount
        if component_row:
            component_row.amount = amount
        else:
            # Add new component
            self.append("earnings", {
                "salary_component": component,
                "amount": amount,
                "default_amount": amount
            })
    
    def make_loan_repayment_entry(self):
        """
        Make loan repayment entry
        """
        # Run standard processing
        super(LebaneseRegulationsSalarySlip, self).make_loan_repayment_entry()
        
        # Add Lebanese-specific processing for loans if needed
        pass
    
    def calculate_lwp_or_ppl_based_amount(self, rule_details, field_to_change):
        """
        Calculate LWP or PPL based amount
        """
        # Run standard calculation
        amount = super(LebaneseRegulationsSalarySlip, self).calculate_lwp_or_ppl_based_amount(rule_details, field_to_change)
        
        # Add Lebanese-specific adjustments if needed
        return amount
    
    def compute_year_to_date(self):
        """
        Compute year to date amounts
        """
        # Run standard computation
        super(LebaneseRegulationsSalarySlip, self).compute_year_to_date()
        
        # Add Lebanese-specific YTD calculations
        self.calculate_nssf_ytd()
        self.calculate_indemnity_ytd()
    
    def calculate_nssf_ytd(self):
        """
        Calculate NSSF year-to-date amounts
        """
        # Get YTD NSSF contributions
        ytd_nssf = frappe.db.sql("""
            SELECT SUM(nssf_employee_contribution) as employee_contribution,
                   SUM(nssf_employer_contribution) as employer_contribution
            FROM `tabSalary Slip`
            WHERE employee = %s
              AND docstatus = 1
              AND start_date >= %s
              AND end_date <= %s
        """, (self.employee, self.year_start_date, self.end_date), as_dict=1)
        
        if ytd_nssf:
            self.nssf_employee_contribution_ytd = flt(ytd_nssf[0].employee_contribution)
            self.nssf_employer_contribution_ytd = flt(ytd_nssf[0].employer_contribution)
            self.total_nssf_contribution_ytd = self.nssf_employee_contribution_ytd + self.nssf_employer_contribution_ytd
    
    def calculate_indemnity_ytd(self):
        """
        Calculate indemnity year-to-date amounts
        """
        # Get YTD indemnity accruals
        ytd_indemnity = frappe.db.sql("""
            SELECT SUM(indemnity_accrual_amount) as indemnity_accrual
            FROM `tabSalary Slip`
            WHERE employee = %s
              AND docstatus = 1
              AND start_date >= %s
              AND end_date <= %s
        """, (self.employee, self.year_start_date, self.end_date), as_dict=1)
        
        if ytd_indemnity:
            self.indemnity_accrual_amount_ytd = flt(ytd_indemnity[0].indemnity_accrual)

# Whitelisted function to override standard make_salary_slip
@frappe.whitelist()
def make_salary_slip(source_name, target_doc=None, employee=None, as_print=False, print_format=None, for_preview=0):
    """
    Create salary slip from salary structure assignment
    """
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