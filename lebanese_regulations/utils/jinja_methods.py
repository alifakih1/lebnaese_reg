# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, cint, cstr
from datetime import datetime
import re

def format_lbp_currency(value, precision=2):
    """
    Format a value as Lebanese Pound (LBP) currency
    
    Args:
        value (float): The value to format
        precision (int): Number of decimal places
        
    Returns:
        str: Formatted currency string with LBP symbol
    """
    if not value:
        return "ل.ل 0.00"
    
    # Get LBP symbol from company settings if available
    lbp_symbol = "ل.ل"
    company = frappe.defaults.get_user_default("Company")
    if company:
        company_symbol = frappe.db.get_value("Company", company, "lbp_currency_symbol")
        if company_symbol:
            lbp_symbol = company_symbol
    
    # Format the number with thousands separator
    formatted_value = "{:,.{prec}f}".format(flt(value), prec=precision)
    
    # Return formatted string with LBP symbol
    return f"{lbp_symbol} {formatted_value}"

def format_arabic_date(date_str, format_str=None):
    """
    Format a date string in Arabic format
    
    Args:
        date_str (str): Date string in YYYY-MM-DD format
        format_str (str): Optional format string
        
    Returns:
        str: Formatted date string in Arabic
    """
    if not date_str:
        return ""
    
    # Default format: DD/MM/YYYY
    if not format_str:
        format_str = "%d/%m/%Y"
    
    # Parse the date string
    if isinstance(date_str, str):
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return date_str
    else:
        date_obj = date_str
    
    # Format the date
    formatted_date = date_obj.strftime(format_str)
    
    # Replace English numerals with Arabic numerals if needed
    if frappe.local.lang == "ar":
        formatted_date = replace_english_with_arabic_numerals(formatted_date)
    
    return formatted_date

def replace_english_with_arabic_numerals(text):
    """
    Replace English numerals with Arabic numerals
    
    Args:
        text (str): Text containing English numerals
        
    Returns:
        str: Text with Arabic numerals
    """
    if not text:
        return ""
    
    # Mapping of English to Arabic numerals
    numeral_map = {
        '0': '٠',
        '1': '١',
        '2': '٢',
        '3': '٣',
        '4': '٤',
        '5': '٥',
        '6': '٦',
        '7': '٧',
        '8': '٨',
        '9': '٩'
    }
    
    # Replace each English numeral with its Arabic equivalent
    for english, arabic in numeral_map.items():
        text = text.replace(english, arabic)
    
    return text

def format_bilingual_text(english_text, arabic_text=None):
    """
    Format text in both English and Arabic
    
    Args:
        english_text (str): Text in English
        arabic_text (str): Text in Arabic
        
    Returns:
        str: Formatted bilingual text
    """
    if not english_text:
        return arabic_text or ""
    
    if not arabic_text:
        return english_text
    
    # Format based on current language
    if frappe.local.lang == "ar":
        return f"{arabic_text} / {english_text}"
    else:
        return f"{english_text} / {arabic_text}"