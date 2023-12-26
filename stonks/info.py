import yfinance as yf
import json
import pandas as pd

def get_income(data, duration):
    if duration:
        value = data.quarterly_income_stmt
    else:
        value = data.income_stmt

    return value

def get_balance(data, duration):
    if duration:
        value = data.quarterly_balance_sheet
    else:
        value = data.balance_sheet

    return value

def get_cashflow(data, duration):
    if duration:
        value = data.quarterly_cashflow
    else:
        value = data.cashflow

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

def get_data(ticker):
    data = yf.Ticker(ticker)

    duration = None

    result = {
        "Ticker": ticker.upper(),
    }

    info = data.info
    result["info"] = info
    balance = get_balance(data, duration)
    result["balance"] = balance
    income = get_income(data, duration)
    result["income"] = income
    cashflow = get_cashflow(data, duration)
    result["cashflow"] = cashflow

    return result

def print_data(ticker, type, duration):
    data = yf.Ticker(ticker)

    pd.set_option('display.max_rows', None)

    result = {}

    if type == 'info':
        return json.dumps(data.info, indent=2)
    
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
