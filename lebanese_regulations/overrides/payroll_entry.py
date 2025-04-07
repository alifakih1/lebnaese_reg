# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, add_days, add_months, get_first_day, get_last_day
from erpnext.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry

class LebaneseRegulationsPayrollEntry(PayrollEntry):
    """
    Customized Payroll Entry for Lebanese regulations
    """
    
    def validate(self):
        """
        Validate payroll entry
        """
        # Run standard validation
        super(LebaneseRegulationsPayrollEntry, self).validate()
        
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
    
    def create_salary_slips(self):
        """
        Create salary slips
        """
        # Run standard creation
        super(LebaneseRegulationsPayrollEntry, self).create_salary_slips()
        
        # Add Lebanese-specific processing
        self.update_nssf_details()
    
    def update_nssf_details(self):
        """
        Update NSSF details in salary slips
        """
        # Get all salary slips created by this payroll entry
        salary_slips = frappe.get_all(
            "Salary Slip",
            filters={
                "payroll_entry": self.name,
                "docstatus": 0
            },
            pluck="name"
        )
        
        if not salary_slips:
            return
        
        # Get company details
        company = frappe.get_doc("Company", self.company)
        nssf_employee_rate = company.get("nssf_employee_rate", 2.0)
        nssf_employer_rate = company.get("nssf_employer_rate", 21.5)
        
        # Update each salary slip
        for slip_name in salary_slips:
            salary_slip = frappe.get_doc("Salary Slip", slip_name)
            
            # Set NSSF rates
            salary_slip.nssf_employee_rate = nssf_employee_rate
            salary_slip.nssf_employer_rate = nssf_employer_rate
            
            # Get employee details
            if salary_slip.employee:
                employee = frappe.get_doc("Employee", salary_slip.employee)
                salary_slip.nssf_number = employee.get("nssf_number", "")
                salary_slip.indemnity_accrual_rate = employee.get("indemnity_accrual_rate", 8.33)
            
            salary_slip.save()
    
    def submit_salary_slips(self):
        """
        Submit salary slips
        """
        # Run standard submission
        super(LebaneseRegulationsPayrollEntry, self).submit_salary_slips()
        
        # Add Lebanese-specific processing
        self.create_nssf_accrual_entry()
        self.create_indemnity_accrual_entry()
    
    def create_nssf_accrual_entry(self):
        """
        Create NSSF accrual journal entry
        """
        # Get all submitted salary slips created by this payroll entry
        salary_slips = frappe.get_all(
            "Salary Slip",
            filters={
                "payroll_entry": self.name,
                "docstatus": 1
            },
            fields=["name", "nssf_employee_contribution", "nssf_employer_contribution", "employee", "company"]
        )
        
        if not salary_slips:
            return
        
        # Calculate total NSSF contributions
        total_employee_contribution = 0
        total_employer_contribution = 0
        
        for slip in salary_slips:
            total_employee_contribution += flt(slip.nssf_employee_contribution)
            total_employer_contribution += flt(slip.nssf_employer_contribution)
        
        total_nssf = total_employee_contribution + total_employer_contribution
        
        if total_nssf <= 0:
            return
        
        # Get company details
        company = frappe.get_doc("Company", self.company)
        nssf_payable_account = company.get("nssf_payable_account")
        
        if not nssf_payable_account:
            frappe.msgprint(_("NSSF Payable Account not configured for company {0}. NSSF accrual entry not created.").format(self.company), 
                           alert=True, indicator="orange")
            return
        
        # Create journal entry
        je = frappe.new_doc("Journal Entry")
        je.posting_date = self.posting_date
        je.company = self.company
        je.user_remark = _("NSSF Accrual for {0}").format(self.name)
        
        # Add employee contribution
        if total_employee_contribution > 0:
            je.append("accounts", {
                "account": self.payroll_payable_account,
                "debit_in_account_currency": total_employee_contribution,
                "reference_type": "Payroll Entry",
                "reference_name": self.name
            })
        
        # Add employer contribution
        if total_employer_contribution > 0:
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
                "debit_in_account_currency": total_employer_contribution,
                "reference_type": "Payroll Entry",
                "reference_name": self.name
            })
        
        # Add NSSF payable
        je.append("accounts", {
            "account": nssf_payable_account,
            "credit_in_account_currency": total_nssf,
            "reference_type": "Payroll Entry",
            "reference_name": self.name
        })
        
        je.insert()
        je.submit()
        
        # Store reference to journal entry
        self.db_set("nssf_accrual_entry", je.name)
        
        frappe.msgprint(_("NSSF Accrual Journal Entry {0} created").format(je.name), 
                       alert=True, indicator="green")
    
    def create_indemnity_accrual_entry(self):
        """
        Create indemnity accrual journal entry
        """
        # Get all submitted salary slips created by this payroll entry
        salary_slips = frappe.get_all(
            "Salary Slip",
            filters={
                "payroll_entry": self.name,
                "docstatus": 1
            },
            fields=["name", "indemnity_accrual_amount", "employee", "company"]
        )
        
        if not salary_slips:
            return
        
        # Calculate total indemnity accrual
        total_indemnity = 0
        
        for slip in salary_slips:
            total_indemnity += flt(slip.indemnity_accrual_amount)
        
        if total_indemnity <= 0:
            return
        
        # Get company details
        company = frappe.get_doc("Company", self.company)
        indemnity_accrual_account = company.get("indemnity_accrual_account")
        
        if not indemnity_accrual_account:
            frappe.msgprint(_("Indemnity Accrual Account not configured for company {0}. Indemnity accrual entry not created.").format(self.company), 
                           alert=True, indicator="orange")
            return
        
        # Create journal entry
        je = frappe.new_doc("Journal Entry")
        je.posting_date = self.posting_date
        je.company = self.company
        je.user_remark = _("Indemnity Accrual for {0}").format(self.name)
        
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
            "debit_in_account_currency": total_indemnity,
            "reference_type": "Payroll Entry",
            "reference_name": self.name
        })
        
        # Add liability
        je.append("accounts", {
            "account": indemnity_accrual_account,
            "credit_in_account_currency": total_indemnity,
            "reference_type": "Payroll Entry",
            "reference_name": self.name
        })
        
        je.insert()
        je.submit()
        
        # Store reference to journal entry
        self.db_set("indemnity_accrual_entry", je.name)
        
        frappe.msgprint(_("Indemnity Accrual Journal Entry {0} created").format(je.name), 
                       alert=True, indicator="green")
    
    def make_accrual_jv_entry(self):
        """
        Make accrual journal entry
        """
        # Run standard accrual entry
        super(LebaneseRegulationsPayrollEntry, self).make_accrual_jv_entry()
        
        # Add Lebanese-specific accrual entries
        self.create_nssf_accrual_entry()
        self.create_indemnity_accrual_entry()
    
    def get_salary_components(self, component_type):
        """
        Get salary components
        """
        # Run standard component retrieval
        components = super(LebaneseRegulationsPayrollEntry, self).get_salary_components(component_type)
        
        # Add Lebanese-specific components if needed
        return components