// Company specific JavaScript for Lebanese Regulations

frappe.ui.form.on('Company', {
    refresh: function(frm) {
        // Add custom buttons or fields for Lebanese regulations
        if (frm.doc.country === 'Lebanon') {
            frm.add_custom_button(__('Setup Lebanese Regulations'), function() {
                // Setup Lebanese regulations for the company
                frappe.msgprint(__('Setting up Lebanese regulations for this company...'));
                
                // Call server-side method to set up defaults
                frappe.call({
                    method: 'lebanese_regulations.setup.setup_company_defaults',
                    args: {
                        company: frm.doc.name
                    },
                    callback: function(r) {
                        frm.reload_doc();
                        frappe.msgprint(__('Lebanese regulations setup completed.'));
                    }
                });
            });
        }
    },
    
    validate: function(frm) {
        // Validate Lebanese-specific fields
        if (frm.doc.country === 'Lebanon') {
            if (!frm.doc.nssf_employer_rate) {
                frm.set_value('nssf_employer_rate', 21.5);
            }
            
            if (!frm.doc.nssf_employee_rate) {
                frm.set_value('nssf_employee_rate', 2.0);
            }
            
            if (!frm.doc.lbp_currency_symbol) {
                frm.set_value('lbp_currency_symbol', 'ل.ل');
            }
        }
    }
});