// Copyright (c) 2023, Your Name and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lebanese Audit Checklist', {
    refresh: function(frm) {
        // Add custom buttons
        if (!frm.is_new() && frm.doc.status !== "Completed") {
            frm.add_custom_button(__('Mark All Completed'), function() {
                frm.call({
                    method: 'mark_all_completed',
                    doc: frm.doc,
                    callback: function(r) {
                        frm.refresh();
                        frappe.show_alert({
                            message: __('All items marked as completed'),
                            indicator: 'green'
                        });
                    }
                });
            });
        }
        
        if (!frm.is_new() && frm.doc.status === "Completed") {
            frm.add_custom_button(__('Generate Report'), function() {
                frm.call({
                    method: 'generate_report',
                    doc: frm.doc,
                    callback: function(r) {
                        if (r.message) {
                            frappe.set_route('Form', 'Lebanese Audit Report', r.message);
                        }
                    }
                });
            });
        }
        
        // Add dashboard
        if (!frm.is_new()) {
            frm.dashboard.add_progress(__('Completion'), frm.doc.completion_percentage);
            
            // Add chart
            frm.dashboard.add_section(
                frappe.render_template('lebanese_audit_checklist_dashboard', {
                    status_counts: get_status_counts(frm.doc),
                    priority_counts: get_priority_counts(frm.doc)
                })
            );
        }
    }
});

// Helper functions for dashboard
function get_status_counts(doc) {
    let counts = {
        'Pending': 0,
        'In Progress': 0,
        'Completed': 0,
        'Not Applicable': 0
    };
    
    if (doc.items) {
        doc.items.forEach(function(item) {
            counts[item.status] = (counts[item.status] || 0) + 1;
        });
    }
    
    return counts;
}

function get_priority_counts(doc) {
    let counts = {
        'Low': 0,
        'Medium': 0,
        'High': 0
    };
    
    if (doc.items) {
        doc.items.forEach(function(item) {
            counts[item.priority] = (counts[item.priority] || 0) + 1;
        });
    }
    
    return counts;
}

// Child table form events
frappe.ui.form.on('Lebanese Audit Checklist Item', {
    status: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        // Auto-fill completion date and user when status is set to Completed
        if (row.status === 'Completed' && !row.completion_date) {
            frappe.model.set_value(cdt, cdn, 'completion_date', frappe.datetime.get_today());
            frappe.model.set_value(cdt, cdn, 'completed_by', frappe.session.user);
        }
        
        // Update parent status and percentage
        frm.trigger('update_status');
    },
    
    items_remove: function(frm) {
        frm.trigger('update_status');
    }
});