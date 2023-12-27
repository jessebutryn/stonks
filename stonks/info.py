import yfinance as yf
import json
import pandas as pd
import requests.exceptions

def get_income(data, duration):
    if duration:
        value = data['quarterly_income_stmt']
    else:
        value = data['income_stmt']

    return value

def get_balance(data, duration):
    if duration:
        value = data['quarterly_balance_sheet']
    else:
        value = data['balance_sheet']

    return value

def get_cashflow(data, duration):
    if duration:
        value = data['quarterly_cashflow']
    else:
        value = data['cashflow']

    return value

def frame_to_json(frame):
    data_list = []

    # Convert index to strings
    frame.index = frame.index.astype(str)

    # Convert column names to strings
    frame.columns = frame.columns.astype(str)

    for column in frame.columns:
        entry = {column: dict(zip(frame.index, frame[column]))}
        data_list.append(entry)

    return json.dumps(data_list, indent=2)

class FinancialData:
    def __init__(self, ticker):
        self.ticker = ticker
        self.fetch_data()

    # def fetch_data(self):
    #     data = yf.Ticker(self.ticker)
    #     self.data = {
    #         'balance_sheet': data.balance_sheet,
    #         'quarterly_balance_sheet': data.quarterly_balance_sheet,
    #         'cashflow': data.cashflow,
    #         'info': data.info,
    #         'income_stmt': data.income_stmt,
    #         'quarterly_income_stmt': data.quarterly_income_stmt
    #     }
    #     return self.data
    def fetch_data(self):
        try:
            data = yf.Ticker(self.ticker)
            self.data = {
                'balance_sheet': data.balance_sheet,
                'quarterly_balance_sheet': data.quarterly_balance_sheet,
                'cashflow': data.cashflow,
                'info': data.info,
                'income_stmt': data.income_stmt,
                'quarterly_income_stmt': data.quarterly_income_stmt
            }
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Error: Ticker '{self.ticker}' not found.")
            else:
                print(f"Error: {e}")
            self.data = None  # Optionally set data to None or handle it as needed

# def get_data(ticker):
#     try:
#         result = {}

#         data = yf.Ticker(ticker)
    
#     except (ValueError, TypeError) as e:
#         return f"No data for: {ticker}"

def print_data(data, type, duration):
    pd.set_option('display.max_rows', None)

    result = {}

    if type == 'info':
        return json.dumps(data['info'], indent=2)
    
    if type == 'balance' or type == 'financials':
        result['balance'] = get_balance(data, duration)

    if type == 'income' or type == 'financials':
        result['income'] = get_income(data, duration)
    
    if type == 'cashflow' or type == 'financials':
        result['cashflow'] = get_cashflow(data, duration)

    combined = pd.concat(result.values(), keys=result.keys())
    combined = combined.reset_index()
    combined = combined.rename(columns={'level_0': 'sheet', 'level_1': 'item'})

    return combined.to_string(index=False)
