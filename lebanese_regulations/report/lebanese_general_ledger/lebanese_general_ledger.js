// Copyright (c) 2023, Your Name and contributors
// For license information, please see license.txt

frappe.query_reports["Lebanese General Ledger"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },
        {
            "fieldname": "finance_book",
            "label": __("Finance Book"),
            "fieldtype": "Link",
            "options": "Finance Book"
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1,
            "width": "60px"
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1,
            "width": "60px"
        },
        {
            "fieldname": "account",
            "label": __("Account"),
            "fieldtype": "Link",
            "options": "Account",
            "get_query": function() {
                var company = frappe.query_report.get_filter_value('company');
                return {
                    "doctype": "Account",
                    "filters": {
                        "company": company,
                    }
                }
            }
        },
        {
            "fieldname": "voucher_no",
            "label": __("Voucher No"),
            "fieldtype": "Data",
            "width": "100px"
        },
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project"
        },
        {
            "fieldname": "party_type",
            "label": __("Party Type"),
            "fieldtype": "Link",
            "options": "Party Type",
            "default": "",
            "on_change": function() {
                frappe.query_report.set_filter_value('party', "");
            }
        },
        {
            "fieldname": "party",
            "label": __("Party"),
            "fieldtype": "MultiSelectList",
            "get_data": function(txt) {
                if (!frappe.query_report.filters) return;

                let party_type = frappe.query_report.get_filter_value('party_type');
                if (!party_type) return;

                return frappe.db.get_link_options(party_type, txt);
            },
            "on_change": function() {
                var party_type = frappe.query_report.get_filter_value('party_type');
                var parties = frappe.query_report.get_filter_value('party');

                if(!party_type || parties.length === 0 || parties.length > 1) {
                    frappe.query_report.set_filter_value('party_name', "");
                    return;
                } else {
                    var party = parties[0];
                    var fieldname = erpnext.utils.get_party_name(party_type) || "name";
                    frappe.db.get_value(party_type, party, fieldname, function(value) {
                        frappe.query_report.set_filter_value('party_name', value[fieldname]);
                    });
                }
            }
        },
        {
            "fieldname": "party_name",
            "label": __("Party Name"),
            "fieldtype": "Data",
            "hidden": 1
        },
        {
            "fieldname": "group_by",
            "label": __("Group by"),
            "fieldtype": "Select",
            "options": ["", __("Group by Voucher"), __("Group by Account"), __("Group by Party")],
            "default": ""
        },
        {
            "fieldname": "cost_center",
            "label": __("Cost Center"),
            "fieldtype": "Link",
            "options": "Cost Center",
            get_query: () => {
                var company = frappe.query_report.get_filter_value('company');
                return {
                    filters: {
                        'company': company
                    }
                };
            }
        },
        {
            "fieldname": "show_in_lbp",
            "label": __("Show in LBP"),
            "fieldtype": "Check",
            "default": 1
        },
        {
            "fieldname": "show_foreign_currency",
            "label": __("Show Foreign Currency"),
            "fieldtype": "Check",
            "default": 1
        },
        {
            "fieldname": "include_dimensions",
            "label": __("Consider Accounting Dimensions"),
            "fieldtype": "Check",
            "default": 1
        },
        {
            "fieldname": "show_cancelled_entries",
            "label": __("Show Cancelled Entries"),
            "fieldtype": "Check"
        },
        {
            "fieldname": "include_default_book_entries",
            "label": __("Include Default Book Entries"),
            "fieldtype": "Check",
            "default": 1
        }
    ],
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (column.fieldname == "debit" && data && data.debit > 0) {
            value = "<span style='color:red'>" + value + "</span>";
        }
        else if (column.fieldname == "credit" && data && data.credit > 0) {
            value = "<span style='color:green'>" + value + "</span>";
        }
        else if (column.fieldname == "debit_lbp" && data && data.debit_lbp > 0) {
            value = "<span style='color:red'>" + value + "</span>";
        }
        else if (column.fieldname == "credit_lbp" && data && data.credit_lbp > 0) {
            value = "<span style='color:green'>" + value + "</span>";
        }
        else if (column.fieldname == "debit_fc" && data && data.debit_fc > 0) {
            value = "<span style='color:red'>" + value + "</span>";
        }
        else if (column.fieldname == "credit_fc" && data && data.credit_fc > 0) {
            value = "<span style='color:green'>" + value + "</span>";
        }
        
        return value;
    },
    "tree": true,
    "name_field": "account",
    "parent_field": "parent_account",
    "initial_depth": 3
};