import yfinance as yf

def get_income(data, duration):
    if duration == 'quarterly':
        value = data.quarterly_income_stmt
    else:
        value = data.income_stmt

    return value

def get_balance(data, duration):
    if duration == 'quarterly':
        value = data.quarterly_balance_sheet
    else:
        value = data.balance_sheet

    return value

def get_cashflow(data, duration):
    if duration == 'quarterly':
        value = data.quarterly_cashflow
    else:
        value = data.cashflow

    return value

def get_data(ticker, type, duration):
    data = yf.Ticker(ticker)

    info = None
    balance = None
    income = None
    cashflow = None

    type_values = type.split()

    if 'info' in type_values or 'all' in type_values:
        info = data.info

        if 'info' in type_values and (balance is None or balance.empty):
            print(f"Error: {ticker} balance sheet data is empty")
            sys.exit(1)

    if 'balance' in type_values or 'all' in type_values:
        balance = get_balance(data, duration)
        
        if 'balance' in type_values and (balance is None or balance.empty):
            print(f"Error: {ticker} balance sheet data is empty")
            sys.exit(1)

    if 'income' in type_values or 'all' in type_values:
        income = get_income(data, duration)

        if 'income' in type_values and (income is None or income.empty):
            print(f"Error: {ticker} income statement data is empty")
            sys.exit(1)

    if 'cashflow' in type_values or 'all' in type_values:
        cashflow = get_cashflow(data, duration)

        if 'cashflow' in type_values and (cashflow is None or cashflow.empty):
            print(f"Error: {ticker} cashflow data is empty")
            sys.exit(1)

    result = {
        'ticker': ticker,
        'info': info,
        'balance': balance,
        'income': income,
        'cashflow': cashflow
    }

    return result
