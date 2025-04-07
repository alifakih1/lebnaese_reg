# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class LebaneseAuditChecklist(Document):
    def validate(self):
        self.update_status_and_percentage()
    
    def update_status_and_percentage(self):
        """
        Update status and completion percentage based on checklist items
        """
        if not self.items:
            self.status = "Not Started"
            self.completion_percentage = 0
            return
        
        total_items = len(self.items)
        completed_items = len([item for item in self.items if item.status == "Completed"])
        
        self.completion_percentage = flt(completed_items) / flt(total_items) * 100 if total_items > 0 else 0
        
        if self.completion_percentage == 0:
            self.status = "Not Started"
        elif self.completion_percentage == 100:
            self.status = "Completed"
        else:
            self.status = "In Progress"
    
    def on_submit(self):
        """
        Validate that all items are either Completed or Not Applicable
        """
        incomplete_items = [item.item for item in self.items 
                           if item.status not in ["Completed", "Not Applicable"]]
        
        if incomplete_items:
            frappe.throw(_("All checklist items must be marked as Completed or Not Applicable before submission. "
                         "The following items are still pending: {0}").format(", ".join(incomplete_items)))
    
    @frappe.whitelist()
    def mark_all_completed(self):
        """
        Mark all checklist items as completed
        """
        for item in self.items:
            if item.status != "Completed":
                item.status = "Completed"
                item.completion_date = frappe.utils.today()
                item.completed_by = frappe.session.user
        
        self.save()
    
    @frappe.whitelist()
    def generate_report(self):
        """
        Generate audit report based on checklist
        """
        # Create a new report
        report = frappe.new_doc("Lebanese Audit Report")
        report.checklist = self.name
        report.company = self.company
        report.fiscal_year = self.fiscal_year
        
        # Add checklist items to report
        for item in self.items:
            report.append("items", {
                "item": item.item,
                "description": item.description,
                "status": item.status,
                "notes": item.notes
            })
        
        report.insert()
        return report.name