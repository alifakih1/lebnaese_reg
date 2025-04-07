# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate, add_months, get_first_day, get_last_day

def process_month_end_exchange_rates():
    """
    Process month-end exchange rates for all currencies against LBP
    This is scheduled to run on the 1st of each month
    """
    # Get previous month's date range
    today = nowdate()
    prev_month_end = add_months(get_first_day(today), 0) - frappe.utils.datetime.timedelta(days=1)
    prev_month_start = get_first_day(prev_month_end)
    
    # Get all active currencies
    currencies = frappe.get_all(
        "Currency",
        filters={"enabled": 1, "name": ["!=", "LBP"]},
        pluck="name"
    )
    
    if not currencies:
        return
    
    # Process each currency
    for currency in currencies:
        # Get the latest exchange rate for the currency against LBP
        latest_rate = get_latest_exchange_rate(currency, prev_month_end)
        
        if not latest_rate:
            frappe.log_error(f"No exchange rate found for {currency}/LBP for {prev_month_end}", 
                            "Month End Exchange Rate Processing")
            continue
        
        # Create a month-end exchange rate record
        create_month_end_exchange_rate(currency, latest_rate, prev_month_end)
        
        # Create revaluation entries for open foreign currency transactions
        create_revaluation_entries(currency, latest_rate, prev_month_end)
    
    frappe.msgprint(_("Month-end exchange rates processed for {0}").format(
        prev_month_end.strftime("%B %Y")
    ))

def get_latest_exchange_rate(currency, date):
    """
    Get the latest exchange rate for a currency against LBP
    
    Args:
        currency: Currency code
        date: Date to get the rate for
        
    Returns:
        float: Exchange rate
    """
    # Try to get direct LBP to currency rate
    exchange_rate = frappe.db.get_value(
        "Currency Exchange",
        {
            "from_currency": "LBP",
            "to_currency": currency,
            "date": ["<=", date]
        },
        "exchange_rate",
        order_by="date desc"
    )
    
    if exchange_rate:
        return flt(exchange_rate)
    
    # Try to get currency to LBP rate
    exchange_rate = frappe.db.get_value(
        "Currency Exchange",
        {
            "from_currency": currency,
            "to_currency": "LBP",
            "date": ["<=", date]
        },
        "exchange_rate",
        order_by="date desc"
    )
    
    if exchange_rate:
        return flt(1.0 / exchange_rate)
    
    # If no direct rate, try to get via base currency (usually USD)
    base_currency = frappe.get_cached_value("Company", {"country": "Lebanon"}, "default_currency") or "USD"
    
    if base_currency != "LBP" and base_currency != currency:
        # Get rate from base currency to LBP
        base_to_lbp = frappe.db.get_value(
            "Currency Exchange",
            {
                "from_currency": base_currency,
                "to_currency": "LBP",
                "date": ["<=", date]
            },
            "exchange_rate",
            order_by="date desc"
        )
        
        # Get rate from base currency to target currency
        base_to_currency = frappe.db.get_value(
            "Currency Exchange",
            {
                "from_currency": base_currency,
                "to_currency": currency,
                "date": ["<=", date]
            },
            "exchange_rate",
            order_by="date desc"
        )
        
        if base_to_lbp and base_to_currency:
            return flt(base_to_lbp / base_to_currency)
    
    return None

def create_month_end_exchange_rate(currency, rate, date):
    """
    Create a month-end exchange rate record
    
    Args:
        currency: Currency code
        rate: Exchange rate
        date: Date for the exchange rate
    """
    # Check if a month-end rate already exists
    existing = frappe.db.exists(
        "Currency Exchange",
        {
            "from_currency": currency,
            "to_currency": "LBP",
            "date": date,
            "for_month_end": 1
        }
    )
    
    if existing:
        # Update existing record
        exchange = frappe.get_doc("Currency Exchange", existing)
        if exchange.exchange_rate != rate:
            exchange.exchange_rate = rate
            exchange.save()
            frappe.msgprint(_("Updated month-end exchange rate for {0}/LBP: {1}").format(
                currency, frappe.format_value(rate, {"fieldtype": "Float", "precision": 4})
            ))
    else:
        # Create new record
        exchange = frappe.new_doc("Currency Exchange")
        exchange.from_currency = currency
        exchange.to_currency = "LBP"
        exchange.exchange_rate = rate
        exchange.date = date
        exchange.for_month_end = 1
        exchange.insert()
        
        frappe.msgprint(_("Created month-end exchange rate for {0}/LBP: {1}").format(
            currency, frappe.format_value(rate, {"fieldtype": "Float", "precision": 4})
        ))

def create_revaluation_entries(currency, rate, date):
    """
    Create revaluation entries for open foreign currency transactions
    
    Args:
        currency: Currency code
        rate: Exchange rate
        date: Date for the revaluation
    """
    # Get all companies with LBP as default currency
    companies = frappe.get_all(
        "Company",
        filters={"default_currency": "LBP"},
        pluck="name"
    )
    
    if not companies:
        return
    
    for company in companies:
        # Check if exchange gain/loss account is set
        exchange_gain_loss_account = frappe.get_cached_value("Company", company, "exchange_gain_loss_account")
        
        if not exchange_gain_loss_account:
            frappe.msgprint(_("Exchange Gain/Loss Account not set for company {0}. Skipping revaluation.").format(company),
                           alert=True, indicator="orange")
            continue
        
        # Get all open GL entries in the foreign currency
        gl_entries = frappe.db.sql("""
            SELECT 
                name, account, party_type, party, 
                account_currency, debit, credit,
                debit_in_account_currency, credit_in_account_currency,
                exchange_rate
            FROM `tabGL Entry`
            WHERE company = %s
              AND account_currency = %s
              AND is_cancelled = 0
              AND posting_date <= %s
        """, (company, currency, date), as_dict=1)
        
        if not gl_entries:
            continue
        
        # Create revaluation entry
        je = frappe.new_doc("Journal Entry")
        je.posting_date = date
        je.company = company
        je.user_remark = _("Revaluation Entry for {0} as of {1}").format(
            currency, date.strftime("%B %Y")
        )
        je.multi_currency = 1
        
        # Process each GL entry
        total_gain_loss = 0
        
        for entry in gl_entries:
            # Calculate the new LBP amount based on the month-end rate
            if entry.debit_in_account_currency > 0:
                original_amount = entry.debit
                foreign_amount = entry.debit_in_account_currency
                new_amount = flt(foreign_amount * rate)
                gain_loss = new_amount - original_amount
            else:
                original_amount = entry.credit
                foreign_amount = entry.credit_in_account_currency
                new_amount = flt(foreign_amount * rate)
                gain_loss = original_amount - new_amount
            
            if abs(gain_loss) < 0.01:
                continue
            
            total_gain_loss += gain_loss
            
            # Add account to journal entry
            account_dict = {
                "account": entry.account,
                "party_type": entry.party_type,
                "party": entry.party,
                "account_currency": entry.account_currency,
                "exchange_rate": rate,
                "reference_type": "GL Entry",
                "reference_name": entry.name
            }
            
            # Set debit or credit based on gain/loss
            if gain_loss > 0:
                account_dict["debit_in_account_currency"] = abs(foreign_amount)
                account_dict["debit"] = abs(gain_loss)
            else:
                account_dict["credit_in_account_currency"] = abs(foreign_amount)
                account_dict["credit"] = abs(gain_loss)
                
            je.append("accounts", account_dict)
        
        # Add exchange gain/loss account to balance the entry
        if abs(total_gain_loss) >= 0.01:
            balance_dict = {
                "account": exchange_gain_loss_account,
                "account_currency": "LBP"
            }
            
            # Set debit or credit based on total gain/loss
            if total_gain_loss < 0:
                balance_dict["debit"] = abs(total_gain_loss)
                balance_dict["debit_in_account_currency"] = abs(total_gain_loss)
            else:
                balance_dict["credit"] = abs(total_gain_loss)
                balance_dict["credit_in_account_currency"] = abs(total_gain_loss)
                
            je.append("accounts", balance_dict)
            
            je.insert()
            je.submit()
            
            frappe.msgprint(_("Created revaluation entry {0} for {1}/{2}").format(
                je.name, currency, company
            ))