# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate

def on_currency_exchange_update(doc, method=None):
    """
    Handle currency exchange rate updates
    
    Args:
        doc: Currency Exchange document
        method: Method name
    """
    # Update all open documents with the new exchange rate
    if doc.from_currency == "LBP" or doc.to_currency == "LBP":
        update_open_documents_with_new_rate(doc)
        
    # Log the exchange rate change
    log_exchange_rate_change(doc)

def update_open_documents_with_new_rate(exchange_doc):
    """
    Update open documents with the new exchange rate
    
    Args:
        exchange_doc: Currency Exchange document
    """
    # Determine which currency is LBP and which is the foreign currency
    if exchange_doc.from_currency == "LBP":
        foreign_currency = exchange_doc.to_currency
        exchange_rate = 1.0 / flt(exchange_doc.exchange_rate)
    else:
        foreign_currency = exchange_doc.from_currency
        exchange_rate = flt(exchange_doc.exchange_rate)
    
    # Update Sales Invoices
    update_sales_invoices(foreign_currency, exchange_rate)
    
    # Update Purchase Invoices
    update_purchase_invoices(foreign_currency, exchange_rate)
    
    # Update Journal Entries
    update_journal_entries(foreign_currency, exchange_rate)
    
    frappe.msgprint(_("Open documents updated with new exchange rate: 1 {0} = {1} LBP").format(
        foreign_currency, frappe.format_value(exchange_rate, {"fieldtype": "Float", "precision": 4})
    ))

def update_sales_invoices(foreign_currency, exchange_rate):
    """
    Update open Sales Invoices with the new exchange rate
    
    Args:
        foreign_currency: Foreign currency code
        exchange_rate: Exchange rate
    """
    # Get all open Sales Invoices in the foreign currency
    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "docstatus": 0,
            "currency": foreign_currency
        },
        pluck="name"
    )
    
    for invoice_name in invoices:
        invoice = frappe.get_doc("Sales Invoice", invoice_name)
        
        # Update exchange rate
        if invoice.get("conversion_rate") != exchange_rate:
            invoice.conversion_rate = exchange_rate
            invoice.save()
            
            frappe.db.commit()
            
            frappe.msgprint(_("Updated exchange rate in Sales Invoice {0}").format(invoice.name))

def update_purchase_invoices(foreign_currency, exchange_rate):
    """
    Update open Purchase Invoices with the new exchange rate
    
    Args:
        foreign_currency: Foreign currency code
        exchange_rate: Exchange rate
    """
    # Get all open Purchase Invoices in the foreign currency
    invoices = frappe.get_all(
        "Purchase Invoice",
        filters={
            "docstatus": 0,
            "currency": foreign_currency
        },
        pluck="name"
    )
    
    for invoice_name in invoices:
        invoice = frappe.get_doc("Purchase Invoice", invoice_name)
        
        # Update exchange rate
        if invoice.get("conversion_rate") != exchange_rate:
            invoice.conversion_rate = exchange_rate
            invoice.save()
            
            frappe.db.commit()
            
            frappe.msgprint(_("Updated exchange rate in Purchase Invoice {0}").format(invoice.name))

def update_journal_entries(foreign_currency, exchange_rate):
    """
    Update open Journal Entries with the new exchange rate
    
    Args:
        foreign_currency: Foreign currency code
        exchange_rate: Exchange rate
    """
    # Get all open Journal Entries with accounts in the foreign currency
    journal_entries = frappe.db.sql("""
        SELECT DISTINCT parent
        FROM `tabJournal Entry Account`
        WHERE docstatus = 0
          AND account_currency = %s
          AND parent IN (SELECT name FROM `tabJournal Entry` WHERE docstatus = 0)
    """, (foreign_currency,), as_dict=1)
    
    for je in journal_entries:
        journal_entry = frappe.get_doc("Journal Entry", je.parent)
        
        # Update exchange rate in accounts
        updated = False
        for account in journal_entry.accounts:
            if account.account_currency == foreign_currency and account.exchange_rate != exchange_rate:
                account.exchange_rate = exchange_rate
                updated = True
        
        if updated:
            journal_entry.save()
            
            frappe.db.commit()
            
            frappe.msgprint(_("Updated exchange rate in Journal Entry {0}").format(journal_entry.name))

def log_exchange_rate_change(exchange_doc):
    """
    Log exchange rate change for audit purposes
    
    Args:
        exchange_doc: Currency Exchange document
    """
    # Create a log entry
    log = frappe.new_doc("Comment")
    log.comment_type = "Info"
    log.reference_doctype = "Currency Exchange"
    log.reference_name = exchange_doc.name
    
    # Format the message
    if exchange_doc.from_currency == "LBP":
        rate_display = f"1 {exchange_doc.to_currency} = {exchange_doc.exchange_rate} LBP"
    else:
        rate_display = f"1 {exchange_doc.from_currency} = {exchange_doc.exchange_rate} {exchange_doc.to_currency}"
    
    log.content = _("Exchange rate updated: {0}").format(rate_display)
    log.save()