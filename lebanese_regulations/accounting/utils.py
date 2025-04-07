# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, get_datetime

def add_currency_info(doc, method=None):
    """
    Add foreign currency information to GL Entry
    """
    if not doc.account_currency or doc.account_currency == "LBP":
        return
    
    # Set foreign currency to account currency
    doc.foreign_currency = doc.account_currency
    doc.foreign_currency_amount = doc.debit_in_account_currency if doc.debit_in_account_currency > 0 else doc.credit_in_account_currency
    
    # Get exchange rate
    if not doc.exchange_rate:
        doc.exchange_rate = get_exchange_rate(doc.account_currency, "LBP", doc.posting_date)
    
    # Calculate LBP amount
    doc.lbp_amount = flt(doc.foreign_currency_amount) * flt(doc.exchange_rate)

def get_exchange_rate(from_currency, to_currency, date):
    """
    Get exchange rate between two currencies
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

def get_account_balance_in_lbp(account, company, posting_date=None):
    """
    Get account balance in LBP
    """
    filters = {
        "account": account,
        "company": company
    }
    
    if posting_date:
        filters["posting_date"] = ("<=", posting_date)
    
    # Get balance in account currency
    balance = frappe.db.sql("""
        SELECT sum(debit_in_account_currency) - sum(credit_in_account_currency) as balance,
               account_currency
        FROM `tabGL Entry`
        WHERE account = %(account)s AND company = %(company)s
        {date_condition}
        GROUP BY account_currency
    """.format(
        date_condition = "AND posting_date <= %(posting_date)s" if posting_date else ""
    ), filters, as_dict=1)
    
    if not balance:
        return 0
    
    # If account currency is LBP, return balance directly
    if balance[0].account_currency == "LBP":
        return balance[0].balance
    
    # Get balance in LBP
    lbp_balance = frappe.db.sql("""
        SELECT sum(lbp_amount) as lbp_balance
        FROM `tabGL Entry`
        WHERE account = %(account)s AND company = %(company)s
        {date_condition}
    """.format(
        date_condition = "AND posting_date <= %(posting_date)s" if posting_date else ""
    ), filters, as_dict=1)
    
    return lbp_balance[0].lbp_balance if lbp_balance and lbp_balance[0].lbp_balance else 0

def get_exchange_gain_loss(account, company, from_date, to_date):
    """
    Calculate exchange gain/loss for an account between two dates
    """
    if not from_date or not to_date:
        return 0
    
    # Get account currency
    account_currency = frappe.db.get_value("Account", account, "account_currency")
    if account_currency == "LBP":
        return 0
    
    # Get balance in account currency at from_date
    opening_balance = get_account_balance(account, company, from_date)
    
    # Get exchange rate at from_date
    opening_exchange_rate = get_exchange_rate(account_currency, "LBP", from_date)
    
    # Get exchange rate at to_date
    closing_exchange_rate = get_exchange_rate(account_currency, "LBP", to_date)
    
    # Calculate exchange gain/loss
    exchange_gain_loss = opening_balance * (closing_exchange_rate - opening_exchange_rate)
    
    return exchange_gain_loss

def get_account_balance(account, company, date=None):
    """
    Get account balance in account currency
    """
    filters = {
        "account": account,
        "company": company
    }
    
    if date:
        filters["posting_date"] = ("<=", date)
    
    # Get balance in account currency
    balance = frappe.db.sql("""
        SELECT sum(debit_in_account_currency) - sum(credit_in_account_currency) as balance
        FROM `tabGL Entry`
        WHERE account = %(account)s AND company = %(company)s
        {date_condition}
    """.format(
        date_condition = "AND posting_date <= %(posting_date)s" if date else ""
    ), filters, as_dict=1)
    
    return balance[0].balance if balance and balance[0].balance else 0