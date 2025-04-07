# Lebanese Regulations User Guide

This guide provides instructions on how to use the Lebanese Regulations module for ERPNext.

## Setup

### 1. Company Configuration

After installing the module, you need to configure your company settings:

1. Go to **Company** doctype and open your company
2. Fill in the following fields:
   - **LBP Currency Symbol**: Default is "ل.ل"
   - **NSSF Employer Contribution Rate**: Default is 21.5%
   - **NSSF Employee Contribution Rate**: Default is 2%
   - **Indemnity Accrual Account**: Select or create an account for End of Service Indemnity accruals
   - **NSSF Payable Account**: Select or create an account for NSSF contributions payable

### 2. Currency Setup

1. Go to **Currency** doctype and ensure "LBP" (Lebanese Pound) is set up
2. Go to **Currency Exchange** doctype and add exchange rates for LBP against other currencies you use

### 3. Chart of Accounts

The module includes a Lebanese Chart of Accounts. To import it:

1. Go to **Company** doctype
2. Click on the **Chart of Accounts** button
3. Select "Import" and choose the file from `apps/lebanese_regulations/lebanese_regulations/setup/data/coa_leb.csv`

### 4. Payroll Configuration

1. Go to **Salary Component** doctype and verify that the following components exist:

   - NSSF Employee Contribution
   - NSSF Employer Contribution
   - End of Service Indemnity

2. Create or update **Salary Structure** to include these components

3. For each **Employee**:
   - Add NSSF Number
   - Set Indemnity Accrual Rate (default: 8.33%)
   - Set Indemnity Start Date (usually the joining date)

## Using Multi-Currency Features

### Lebanese General Ledger

The module provides a multi-currency General Ledger report:

1. Go to **Lebanese General Ledger** report
2. Use the filters to select:
   - Company
   - Date range
   - Accounts
   - Show in LBP: Toggle to show LBP amounts
   - Show Foreign Currency: Toggle to show foreign currency amounts

### Other Financial Reports

The standard financial reports have been enhanced to support multi-currency:

1. **Trial Balance**: Shows account balances in both account currency and LBP
2. **Balance Sheet**: Aggregates values in LBP with foreign currency breakdowns
3. **Profit and Loss Statement**: Shows values in LBP with foreign currency details

## Compliance Features

### Lebanese Audit Checklist

1. Go to **Lebanese Audit Checklist** doctype
2. Create a new checklist for your company and fiscal year
3. Track compliance items:

   - NSSF Compliance
   - End of Service Indemnity Accruals
   - Multi-Currency Reconciliation
   - Lebanese GAAP Compliance
   - Income Tax Calculation

4. Update the status of each item as you complete them
5. Generate a compliance report when all items are completed

### NSSF Deadline Reminders

The system automatically sends reminders for NSSF submission deadlines:

1. Reminders are sent 5, 3, and 1 day before the deadline
2. Notifications are sent to users with the "Compliance Manager" role
3. The deadline is set to the 15th of each month for the previous month's contributions

## Bilingual Features

The module supports bilingual (Arabic/English) features:

1. **Date Formatting**: Dates are formatted according to Lebanese standards (DD/MM/YYYY)
2. **Currency Formatting**: LBP amounts are displayed with the proper symbol (ل.ل)
3. **Address Formatting**: Addresses can be stored and displayed in both Arabic and English

## Troubleshooting

If you encounter issues:

1. **Exchange Rates**: Ensure you have up-to-date exchange rates in the Currency Exchange doctype
2. **NSSF Calculations**: Verify the NSSF rates in Company settings
3. **Indemnity Accruals**: Check that employees have the correct indemnity accrual rate and start date
4. **Multi-Currency Reports**: Ensure all transactions have the correct exchange rates

For further assistance, please contact support.
