# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json

def after_request(response):
    """
    Handle after request events
    
    Args:
        response: Response object
    """
    # Add Arabic language support for responses
    add_arabic_language_support(response)
    
    return response

def add_arabic_language_support(response):
    """
    Add Arabic language support for responses
    
    Args:
        response: Response object
    """
    # Check if response is JSON
    if not response.headers.get("Content-Type", "").startswith("application/json"):
        return
    
    # Check if user prefers Arabic
    user = frappe.session.user
    
    if not user or user == "Guest":
        return
    
    # Check if user language is Arabic
    user_language = frappe.db.get_value("User", user, "language")
    
    if user_language != "ar":
        return
    
    try:
        # Parse response data
        data = json.loads(response.get_data(as_text=True))
        
        # Add RTL direction for Arabic
        if isinstance(data, dict):
            data["dir"] = "rtl"
            
            # Convert response back to JSON
            response.set_data(json.dumps(data))
    except Exception:
        # If any error occurs, just return the original response
        pass