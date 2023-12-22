#!/usr/bin/env python3
import yfinance as yf
import sys
import pandas as pd
import json

def display_financial_data(symbol, data_type):
    try:
        # Download financial statements
        stock_data = yf.Ticker(symbol)

        # Get the specified financial data
        if data_type == 'info':
            data = json.dumps(stock_data.info)
            print(data)
            return
        elif data_type == 'income_statement':
            data = stock_data.financials
        elif data_type == 'balance_sheet':
            data = stock_data.balance_sheet
        elif data_type == 'cash_flow':
            data = stock_data.cashflow
        elif data_type == 'dividends':
            data = stock_data.dividends
        else:
            print(f"Invalid data type. Choose from 'info', 'income_statement', 'balance_sheet', 'cash_flow', 'dividends'")
            return

        # Display the selected financial data without shape information
        print(f"{data_type}:\n")
        print(data.to_string(index=True, max_rows=None))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Check if both stock symbol and data type are provided as positional parameters
    if len(sys.argv) != 3:
        print("Usage: python financial_data.py <stock_symbol> <data_type>")
        sys.exit(1)

    stock_symbol = sys.argv[1]
    data_type = sys.argv[2].lower()

    display_financial_data(stock_symbol, data_type)
