// Lebanese Regulations Web JavaScript

// Format LBP currency with proper symbol
function format_lbp_currency(value, precision) {
    precision = precision || 0;
    value = parseFloat(value).toFixed(precision);
    
    // Use default LBP symbol
    let symbol = "ل.ل";
    
    return value + " " + symbol;
}

// Format date in Lebanese format (DD/MM/YYYY)
function format_lebanese_date(date_str) {
    if (!date_str) return "";
    let date = new Date(date_str);
    let day = date.getDate().toString().padStart(2, '0');
    let month = (date.getMonth() + 1).toString().padStart(2, '0');
    let year = date.getFullYear();
    
    return day + "/" + month + "/" + year;
}

// Replace English numerals with Arabic numerals
function replace_english_with_arabic_numerals(text) {
    if (!text) return "";
    
    const english_numerals = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
    const arabic_numerals = ["٠", "١", "٢", "٣", "٤", "٥", "٦", "٧", "٨", "٩"];
    
    for (let i = 0; i < english_numerals.length; i++) {
        text = text.replace(new RegExp(english_numerals[i], "g"), arabic_numerals[i]);
    }
    
    return text;
}

// Initialize Lebanese Regulations Web
$(document).ready(function() {
    // Apply Lebanese formatting to elements with specific classes
    $('.leb-currency').each(function() {
        let value = $(this).text();
        $(this).text(format_lbp_currency(value));
    });
    
    $('.leb-date').each(function() {
        let value = $(this).text();
        $(this).text(format_lebanese_date(value));
    });
    
    $('.leb-arabic-numerals').each(function() {
        let value = $(this).text();
        $(this).text(replace_english_with_arabic_numerals(value));
    });
});