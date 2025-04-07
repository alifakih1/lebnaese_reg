# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
import time

def after_job(job, status, duration=None):
    """
    Handle after job events
    
    Args:
        job: Job object
        status: Job status
        duration: Job duration
    """
    # Log job completion for Lebanese-specific jobs
    if is_lebanese_job(job):
        log_lebanese_job_completion(job, status, duration)

def is_lebanese_job(job):
    """
    Check if job is a Lebanese-specific job
    
    Args:
        job: Job object
        
    Returns:
        bool: True if job is Lebanese-specific
    """
    # Check if job method is from lebanese_regulations module
    return job.method and "lebanese_regulations" in job.method

def log_lebanese_job_completion(job, status, duration=None):
    """
    Log job completion for Lebanese-specific jobs
    
    Args:
        job: Job object
        status: Job status
        duration: Job duration
    """
    # Calculate duration if not provided
    if duration is None:
        # Try to get start time from job
        start_time = getattr(job, "start_time", None)
        
        if start_time:
            duration = time.time() - start_time
        else:
            duration = 0
    
    frappe.logger().info(f"Completed Lebanese job: {job.method} with status {status} in {duration:.2f}s")
    
    # Create a log entry
    log = frappe.new_doc("Error Log")
    log.method = job.method
    log.error_type = "Lebanese Job Completion"
    log.error = f"Completed Lebanese job: {job.method} with status {status}"
    
    # Add job details
    job_details = {
        "job_name": job.name,
        "job_type": job.job_type,
        "job_method": job.method,
        "job_status": status,
        "job_duration": f"{duration:.2f}s" if duration else "Unknown"
    }
    
    log.error_description = json.dumps(job_details, indent=2)
    log.insert(ignore_permissions=True)
    
    # If job failed, send notification to administrators
    if status == "failed":
        send_job_failure_notification(job, job_details)

def send_job_failure_notification(job, job_details):
    """
    Send notification about job failure
    
    Args:
        job: Job object
        job_details: Job details
    """
    # Get system managers
    system_managers = frappe.db.sql_list("""
        SELECT DISTINCT u.email
        FROM `tabUser` u
        JOIN `tabHas Role` r ON r.parent = u.name
        WHERE r.role = 'System Manager'
          AND u.enabled = 1
          AND u.email IS NOT NULL
          AND u.email != ''
    """)
    
    if not system_managers:
        return
    
    # Create notification
    subject = _("Lebanese Job Failed: {0}").format(job.method)
    
    message = _("A Lebanese-specific job has failed:")
    message += "<br><br>"
    message += f"<b>{_('Method')}:</b> {job.method}<br>"
    message += f"<b>{_('Job Type')}:</b> {job.job_type}<br>"
    message += f"<b>{_('Duration')}:</b> {job_details.get('job_duration', 'Unknown')}<br>"
    message += "<br>"
    message += _("Please check the Error Log for more details.")
    
    # Send notification
    frappe.sendmail(
        recipients=system_managers,
        subject=subject,
        message=message,
        reference_doctype="Error Log",
        reference_name=job.name
    )