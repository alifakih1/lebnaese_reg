# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

def update_itemised_tax_data(doc):
    """
    Update itemised tax data for Lebanese tax reporting
    """
    # Add LBP amounts to tax data
    if not doc.taxes:
        return
    
    # Get exchange rate if needed
    exchange_rate = 1.0
    if doc.currency and doc.currency != "LBP":
        exchange_rate = doc.conversion_rate or 1.0
    
    for tax in doc.taxes:
        if not tax.item_wise_tax_detail:
            continue
        
        item_tax_map = frappe.parse_json(tax.item_wise_tax_detail)
        
        for item_code, tax_data in item_tax_map.items():
            tax_rate, tax_amount = tax_data
            
            # Add LBP amount
            if doc.currency and doc.currency != "LBP":
                lbp_amount = flt(tax_amount) * flt(exchange_rate)
                item_tax_map[item_code] = [tax_rate, tax_amount, lbp_amount]
        
        tax.item_wise_tax_detail = frappe.as_json(item_tax_map)

def get_regional_address_details(address, doctype, company):
    """
    Return regional address details for Lebanon
    """
    address_details = frappe._dict()
    
    if not address:
        return address_details
    
    address_doc = frappe.get_doc("Address", address)
    
    # Format address for Lebanon
    address_details.address_line1 = address_doc.address_line1 or ""
    address_details.address_line2 = address_doc.address_line2 or ""
    address_details.city = address_doc.city or ""
    address_details.state = address_doc.state or ""
    address_details.country = address_doc.country or ""
    address_details.postal_code = address_doc.pincode or ""
    
    # Add Arabic address if available
    address_details.address_line1_ar = address_doc.get("address_line1_ar", "")
    address_details.address_line2_ar = address_doc.get("address_line2_ar", "")
    address_details.city_ar = address_doc.get("city_ar", "")
    
    return address_details

def get_regional_round_off_accounts(company, account_data, round_off_cost_center):
    """
    Return round off accounts for Lebanon
    """
    # Get company default currency
    company_currency = frappe.get_cached_value("Company", company, "default_currency")
    
    # If company currency is LBP, use standard round off account
    if company_currency == "LBP":
        return account_data
    
    # For multi-currency, use exchange gain/loss account
    exchange_gain_loss_account = frappe.get_cached_value("Company", company, "exchange_gain_loss_account")
    
    if exchange_gain_loss_account:
        account_data.round_off_account = exchange_gain_loss_account
    
    return account_data