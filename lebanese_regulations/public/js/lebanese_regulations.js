// Lebanese Regulations JavaScript

frappe.provide("lebanese_regulations");

lebanese_regulations = {
    // Format LBP currency with proper symbol
    format_lbp_currency: function(value, precision) {
        precision = precision || 0;
        value = flt(value, precision);
        
        // Get LBP symbol from company settings or use default
        let symbol = "ل.ل";
        if (frappe.boot.company_currency_symbols && frappe.boot.company_currency_symbols["LBP"]) {
            symbol = frappe.boot.company_currency_symbols["LBP"];
        }
        
        return format_currency(value, "LBP", precision) + " " + symbol;
    },
    
    // Format date in Lebanese format (DD/MM/YYYY)
    format_lebanese_date: function(date_str) {
        if (!date_str) return "";
        let date = frappe.datetime.str_to_obj(date_str);
        return frappe.datetime.str_to_user(date_str, "dd/MM/yyyy");
    },
    
    // Replace English numerals with Arabic numerals
    replace_english_with_arabic_numerals: function(text) {
        if (!text) return "";
        
        const english_numerals = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
        const arabic_numerals = ["٠", "١", "٢", "٣", "٤", "٥", "٦", "٧", "٨", "٩"];
        
        for (let i = 0; i < english_numerals.length; i++) {
            text = text.replace(new RegExp(english_numerals[i], "g"), arabic_numerals[i]);
        }
        
        return text;
    }
};

// Initialize Lebanese Regulations
$(document).ready(function() {
    // Add custom formatters
    frappe.form.formatters.LBP = function(value, df) {
        return lebanese_regulations.format_lbp_currency(value);
    };
});