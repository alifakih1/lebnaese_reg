# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, flt, cstr
from erpnext.accounts.report.general_ledger.general_ledger import execute as gl_execute

def execute(filters=None):
    """
    Execute the Lebanese General Ledger report
    
    Args:
        filters (dict): Report filters
        
    Returns:
        tuple: (columns, data)
    """
    # Add default filters for Lebanese GL
    if not filters:
        filters = {}
    
    # Add show_in_lbp filter if not present
    if "show_in_lbp" not in filters:
        filters["show_in_lbp"] = 1
    
    # Add show_foreign_currency filter if not present
    if "show_foreign_currency" not in filters:
        filters["show_foreign_currency"] = 1
    
    # Execute standard GL report
    columns, data = gl_execute(filters)
    
    # Modify columns and data for Lebanese requirements
    columns, data = modify_for_lebanese_requirements(filters, columns, data)
    
    return columns, data

def modify_for_lebanese_requirements(filters, columns, data):
    """
    Modify columns and data for Lebanese requirements
    
    Args:
        filters (dict): Report filters
        columns (list): Report columns
        data (list): Report data
        
    Returns:
        tuple: (columns, data)
    """
    # Add LBP and foreign currency columns if needed
    if filters.get("show_in_lbp"):
        # Add LBP columns
        columns = add_lbp_columns(columns)
        
        # Add LBP values to data
        data = add_lbp_values(data, filters)
    
    # Add foreign currency columns if needed
    if filters.get("show_foreign_currency"):
        # Add foreign currency columns
        columns = add_foreign_currency_columns(columns)
        
        # Add foreign currency values to data
        data = add_foreign_currency_values(data, filters)
    
    return columns, data

def add_lbp_columns(columns):
    """
    Add LBP columns to the report
    
    Args:
        columns (list): Report columns
        
    Returns:
        list: Modified columns
    """
    # Find the position to insert LBP columns
    debit_idx = -1
    credit_idx = -1
    
    for i, col in enumerate(columns):
        if col.get("fieldname") == "debit":
            debit_idx = i
        elif col.get("fieldname") == "credit":
            credit_idx = i
    
    if debit_idx >= 0 and credit_idx >= 0:
        # Insert LBP columns after debit and credit
        lbp_columns = [
            {
                "label": _("Debit (LBP)"),
                "fieldname": "debit_lbp",
                "fieldtype": "Currency",
                "options": "LBP",
                "width": 120
            },
            {
                "label": _("Credit (LBP)"),
                "fieldname": "credit_lbp",
                "fieldtype": "Currency",
                "options": "LBP",
                "width": 120
            }
        ]
        
        # Insert after credit column
        columns.insert(credit_idx + 1, lbp_columns[1])
        columns.insert(debit_idx + 1, lbp_columns[0])
    
    return columns

def add_foreign_currency_columns(columns):
    """
    Add foreign currency columns to the report
    
    Args:
        columns (list): Report columns
        
    Returns:
        list: Modified columns
    """
    # Find the position to insert foreign currency columns
    debit_idx = -1
    credit_idx = -1
    
    for i, col in enumerate(columns):
        if col.get("fieldname") == "debit":
            debit_idx = i
        elif col.get("fieldname") == "credit":
            credit_idx = i
    
    if debit_idx >= 0 and credit_idx >= 0:
        # Insert foreign currency columns
        fc_columns = [
            {
                "label": _("Foreign Currency"),
                "fieldname": "foreign_currency",
                "fieldtype": "Link",
                "options": "Currency",
                "width": 100
            },
            {
                "label": _("Exchange Rate"),
                "fieldname": "exchange_rate",
                "fieldtype": "Float",
                "precision": 6,
                "width": 100
            },
            {
                "label": _("Debit (FC)"),
                "fieldname": "debit_fc",
                "fieldtype": "Currency",
                "options": "foreign_currency",
                "width": 120
            },
            {
                "label": _("Credit (FC)"),
                "fieldname": "credit_fc",
                "fieldtype": "Currency",
                "options": "foreign_currency",
                "width": 120
            }
        ]
        
        # Insert before debit column
        for i, col in enumerate(fc_columns):
            columns.insert(debit_idx + i, col)
    
    return columns

def add_lbp_values(data, filters):
    """
    Add LBP values to the report data
    
    Args:
        data (list): Report data
        filters (dict): Report filters
        
    Returns:
        list: Modified data
    """
    for row in data:
        if not row.get("posting_date"):
            continue
        
        # Get exchange rate
        exchange_rate = 1.0
        if row.get("account_currency") and row.get("account_currency") != "LBP":
            exchange_rate = get_exchange_rate(row.get("account_currency"), "LBP", row.get("posting_date"))
        
        # Calculate LBP values
        row["debit_lbp"] = flt(row.get("debit")) * flt(exchange_rate)
        row["credit_lbp"] = flt(row.get("credit")) * flt(exchange_rate)
    
    return data

def add_foreign_currency_values(data, filters):
    """
    Add foreign currency values to the report data
    
    Args:
        data (list): Report data
        filters (dict): Report filters
        
    Returns:
        list: Modified data
    """
    for row in data:
        if not row.get("posting_date"):
            continue
        
        # Set foreign currency values
        if row.get("account_currency") and row.get("account_currency") != "LBP":
            row["foreign_currency"] = row.get("account_currency")
            row["exchange_rate"] = get_exchange_rate(row.get("account_currency"), "LBP", row.get("posting_date"))
            
            # Calculate foreign currency values
            if row.get("debit") > 0:
                row["debit_fc"] = flt(row.get("debit_in_account_currency"))
                row["credit_fc"] = 0
            else:
                row["debit_fc"] = 0
                row["credit_fc"] = flt(row.get("credit_in_account_currency"))
        else:
            # For LBP accounts, set foreign currency values to zero
            row["foreign_currency"] = ""
            row["exchange_rate"] = 1.0
            row["debit_fc"] = 0
            row["credit_fc"] = 0
    
    return data

def get_exchange_rate(from_currency, to_currency, date):
    """
    Get exchange rate between two currencies
    
    Args:
        from_currency (str): From currency
        to_currency (str): To currency
        date (str): Date for exchange rate
        
    Returns:
        float: Exchange rate
    """
    if from_currency == to_currency:
        return 1.0
    
    # Get exchange rate from Currency Exchange
    exchange_rate = frappe.db.get_value("Currency Exchange",
        {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "date": ("<=", date)
        },
        "exchange_rate",
        order_by="date desc"
    )
    
    if not exchange_rate:
        # Try reverse lookup
        exchange_rate = frappe.db.get_value("Currency Exchange",
            {
                "from_currency": to_currency,
                "to_currency": from_currency,
                "date": ("<=", date)
            },
            "exchange_rate",
            order_by="date desc"
        )
        
        if exchange_rate:
            exchange_rate = 1.0 / flt(exchange_rate)
    
    return exchange_rate or 1.0