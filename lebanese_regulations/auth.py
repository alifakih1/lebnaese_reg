# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint

def validate(login_manager):
    """
    Validate user login
    
    Args:
        login_manager: Login Manager object
    """
    # Check if user is from Lebanon
    if is_lebanese_user(login_manager.user):
        # Apply Lebanese-specific validations
        validate_lebanese_user(login_manager)

def is_lebanese_user(user):
    """
    Check if user is from Lebanon
    
    Args:
        user: User name
        
    Returns:
        bool: True if user is from Lebanon
    """
    # Check user country
    user_country = frappe.db.get_value("User", user, "country")
    
    return user_country == "Lebanon"

def validate_lebanese_user(login_manager):
    """
    Validate Lebanese user
    
    Args:
        login_manager: Login Manager object
    """
    # Check if user has access to Lebanese Regulations module
    if not has_lebanese_regulations_access(login_manager.user):
        # Add Lebanese Regulations module access
        add_lebanese_regulations_access(login_manager.user)
    
    # Set default language to Arabic if not set
    set_default_language(login_manager.user)
    
    # Set default date format to DD/MM/YYYY
    set_default_date_format(login_manager.user)

def has_lebanese_regulations_access(user):
    """
    Check if user has access to Lebanese Regulations module
    
    Args:
        user: User name
        
    Returns:
        bool: True if user has access
    """
    # Check if user has Lebanese Regulations in allowed modules
    allowed_modules = frappe.get_all(
        "User Module",
        filters={
            "parent": user,
            "module": "Lebanese Regulations"
        },
        limit=1
    )
    
    return bool(allowed_modules)

def add_lebanese_regulations_access(user):
    """
    Add Lebanese Regulations module access to user
    
    Args:
        user: User name
    """
    # Get user doc
    user_doc = frappe.get_doc("User", user)
    
    # Check if module already exists
    for module in user_doc.get("block_modules", []):
        if module.module == "Lebanese Regulations":
            return
    
    # Add module access
    user_doc.append("allowed_modules", {
        "module": "Lebanese Regulations"
    })
    
    # Save user
    user_doc.save(ignore_permissions=True)
    
    frappe.msgprint(_("Lebanese Regulations module access added for user {0}").format(user))

def set_default_language(user):
    """
    Set default language to Arabic if not set
    
    Args:
        user: User name
    """
    # Get current language
    current_language = frappe.db.get_value("User", user, "language")
    
    # If language not set, set to Arabic
    if not current_language:
        frappe.db.set_value("User", user, "language", "ar")
        
        frappe.msgprint(_("Default language set to Arabic for user {0}").format(user))

def set_default_date_format(user):
    """
    Set default date format to DD/MM/YYYY
    
    Args:
        user: User name
    """
    # Get current date format
    current_format = frappe.db.get_value("User", user, "date_format")
    
    # If not DD/MM/YYYY, set it
    if current_format != "dd/mm/yyyy":
        frappe.db.set_value("User", user, "date_format", "dd/mm/yyyy")
        
        frappe.msgprint(_("Default date format set to DD/MM/YYYY for user {0}").format(user))