#!/usr/bin/env python3
import yfinance as yf
import sys
import json

def print_data(symbol, data_type):
    try:
        stock_data = yf.Ticker(symbol)

        if data_type == 'info':
            py_data = stock_data.info
            data = json.dumps(py_data, indent=2)
        elif data_type == 'income_statement':
            pd_data = stock_data.income_stmt
            data = pd_data.to_json(orient="columns")
        elif data_type == 'balance_sheet':
            pd_data = stock_data.balance_sheet
            data = pd_data.to_json(orient="columns")
        elif data_type == 'cash_flow':
            pd_data = stock_data.cashflow
            data = pd_data.to_json(orient="columns")
        elif data_type == 'dividends':
            pd_data = stock_data.dividends
            data = pd_data.to_json(orient="columns")
        else:
            print(f"Invalid data type. Choose from 'info', 'income_statement', 'balance_sheet', 'cash_flow', 'dividends'")
            return

        print(data)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python financial_data.py <stock_symbol> <data_type>")
        sys.exit(1)

    stock_symbol = sys.argv[1]
    data_type = sys.argv[2].lower()
    

print_data(stock_symbol, data_type)
