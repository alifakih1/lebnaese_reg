# -*- coding: utf-8 -*-
# Copyright (c) 2023, Your Name and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json

def before_job(job):
    """
    Handle before job events
    
    Args:
        job: Job object
    """
    # Log job start for Lebanese-specific jobs
    if is_lebanese_job(job):
        log_lebanese_job_start(job)

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

def log_lebanese_job_start(job):
    """
    Log job start for Lebanese-specific jobs
    
    Args:
        job: Job object
    """
    frappe.logger().info(f"Starting Lebanese job: {job.method}")
    
    # Create a log entry
    log = frappe.new_doc("Error Log")
    log.method = job.method
    log.error_type = "Lebanese Job Start"
    log.error = f"Starting Lebanese job: {job.method}"
    
    # Add job details
    job_details = {
        "job_name": job.name,
        "job_type": job.job_type,
        "job_method": job.method,
        "job_arguments": job.kwargs
    }
    
    log.error_description = json.dumps(job_details, indent=2)
    log.insert(ignore_permissions=True)