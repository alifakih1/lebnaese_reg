# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_request_session

def before_request(request):
    """
    Handle before request events
    
    Args:
        request: Request object
    """
    # Set default date format for Lebanese users
    set_lebanese_date_format()
    
    # Set LBP currency formatting
    set_lbp_currency_formatting()

def set_lebanese_date_format():
    """
    Set default date format to DD/MM/YYYY for Lebanese users
    """
    user = frappe.session.user
    
    if not user or user == "Guest":
        return
    
    # Check if user is from Lebanon
    user_country = frappe.db.get_value("User", user, "country")
    
    if user_country == "Lebanon":
        # Set date format to DD/MM/YYYY
        frappe.db.set_value("User", user, "date_format", "dd/mm/yyyy")

def set_lbp_currency_formatting():
    """
    Set LBP currency formatting
    """
    # Check if LBP currency exists
    if not frappe.db.exists("Currency", "LBP"):
        return
    
    # Get LBP currency
    lbp = frappe.get_doc("Currency", "LBP")
    
    # Set LBP formatting if not already set
    if lbp.symbol != "ل.ل" or lbp.fraction != "" or lbp.fraction_units != 0:
        lbp.symbol = "ل.ل"
        lbp.fraction = ""  # No fraction for LBP
        lbp.fraction_units = 0  # No fraction units for LBP
        lbp.number_format = "#,###.##"
        lbp.smallest_currency_fraction_value = 250  # Smallest LBP coin is 250
        
        # Save changes
        lbp.db_update()
        frappe.clear_cache()