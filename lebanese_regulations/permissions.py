# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.permissions import add_user_permission, remove_user_permission

def get_permission_query_conditions_for_audit_checklist(user):
    """
    Get permission query conditions for Lebanese Audit Checklist
    
    Args:
        user: User name
        
    Returns:
        str: Query conditions
    """
    if not user:
        return ""
    
    # If user is System Manager, no conditions
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    # If user is Compliance Manager, show all checklists
    if "Compliance Manager" in frappe.get_roles(user):
        return ""
    
    # For other users, show only checklists they own or are assigned to
    conditions = []
    
    # Checklists owned by the user
    conditions.append(f"`tabLebanese Audit Checklist`.owner = '{user}'")
    
    # Checklists where user is assigned
    conditions.append(f"`tabLebanese Audit Checklist`.assigned_to = '{user}'")
    
    # Checklists for companies where user has permissions
    user_companies = get_user_companies(user)
    if user_companies:
        company_condition = "`tabLebanese Audit Checklist`.company in ({})".format(
            ", ".join([f"'{company}'" for company in user_companies])
        )
        conditions.append(company_condition)
    
    return "(" + " OR ".join(conditions) + ")"

def has_permission_for_audit_checklist(doc, user=None, permission_type=None):
    """
    Check if user has permission for Lebanese Audit Checklist
    
    Args:
        doc: Document
        user: User name
        permission_type: Permission type
        
    Returns:
        bool: True if user has permission
    """
    if not user:
        user = frappe.session.user
    
    # If user is System Manager, allow all
    if "System Manager" in frappe.get_roles(user):
        return True
    
    # If user is Compliance Manager, allow all
    if "Compliance Manager" in frappe.get_roles(user):
        return True
    
    # If user is owner, allow
    if doc.owner == user:
        return True
    
    # If user is assigned, allow
    if doc.assigned_to == user:
        return True
    
    # If user has permission for the company, allow
    user_companies = get_user_companies(user)
    if doc.company in user_companies:
        return True
    
    return False

def get_user_companies(user):
    """
    Get companies for which user has permissions
    
    Args:
        user: User name
        
    Returns:
        list: List of companies
    """
    # Get companies from User Permission
    user_permissions = frappe.get_all(
        "User Permission",
        filters={
            "user": user,
            "allow": "Company"
        },
        fields=["for_value"]
    )
    
    companies = [p.for_value for p in user_permissions]
    
    # If no specific permissions, check if user has Employee linked to a company
    if not companies:
        employee = frappe.db.exists("Employee", {"user_id": user})
        if employee:
            company = frappe.db.get_value("Employee", employee, "company")
            if company:
                companies.append(company)
    
    return companies

def setup_audit_checklist_permissions(doc, method=None):
    """
    Set up permissions for Lebanese Audit Checklist
    
    Args:
        doc: Document
        method: Method name
    """
    # Add permission for the assigned user
    if doc.assigned_to and doc.assigned_to != doc.owner:
        add_user_permission("Lebanese Audit Checklist", doc.name, doc.assigned_to)
    
    # Add permission for Compliance Managers
    compliance_managers = get_users_with_role("Compliance Manager")
    for user in compliance_managers:
        if user != doc.owner and user != doc.assigned_to:
            add_user_permission("Lebanese Audit Checklist", doc.name, user)

def cleanup_audit_checklist_permissions(doc, method=None):
    """
    Clean up permissions for Lebanese Audit Checklist
    
    Args:
        doc: Document
        method: Method name
    """
    # Remove all user permissions for this document
    user_permissions = frappe.get_all(
        "User Permission",
        filters={
            "allow": "Lebanese Audit Checklist",
            "for_value": doc.name
        },
        fields=["name", "user"]
    )
    
    for permission in user_permissions:
        remove_user_permission("Lebanese Audit Checklist", doc.name, permission.user)

def get_users_with_role(role):
    """
    Get all users with a specific role
    
    Args:
        role: Role name
        
    Returns:
        list: List of user names
    """
    return frappe.db.sql_list("""
        SELECT DISTINCT u.name
        FROM `tabUser` u
        JOIN `tabHas Role` r ON r.parent = u.name
        WHERE r.role = %s
          AND u.enabled = 1
    """, role)