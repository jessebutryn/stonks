import re

# def format_currency(value):
#     value = float(value)
    
#     suffixes = ['', 'K', 'M', 'B', 'T', 'Q']
#     order_of_magnitude = 0
    
#     while value >= 1000 and order_of_magnitude < len(suffixes) - 1:
#         value /= 1000.0
#         order_of_magnitude += 1
    
#     formatted_value = f'{value:.2f}'
    
#     if '.' in formatted_value and formatted_value.endswith('00'):
#         # Remove unnecessary '.00'
#         formatted_value = formatted_value[:-3]
    
#     return f'{formatted_value}{suffixes[order_of_magnitude]}'

def format_currency(value):
    value = float(value)
    
    # Determine the sign of the value
    sign = '-' if value < 0 else ''
    
    # Take the absolute value for processing
    abs_value = abs(value)

    suffixes = ['', 'K', 'M', 'B', 'T', 'Q']
    order_of_magnitude = 0
    
    while abs_value >= 1000 and order_of_magnitude < len(suffixes) - 1:
        abs_value /= 1000.0
        order_of_magnitude += 1
    
    formatted_value = f'{abs_value:.2f}'
    
    if '.' in formatted_value and formatted_value.endswith('00'):
        # Remove unnecessary '.00'
        formatted_value = formatted_value[:-3]
    
    return f'{sign}{formatted_value}{suffixes[order_of_magnitude]}'

def debt_to_equity(balance):
    latest_date = balance.columns.max()
    latest_balance = balance[latest_date]
    
    debt = latest_balance.get('Total Debt', None)
    equity = latest_balance.get('Stockholders Equity', 'NaN')

    if debt is None:
        return latest_balance.get('Total Liabilities Net Minority Interest', 'N/A')

    try:
        debt = float(debt)
        equity = float(equity)

        if equity == 0:
            raise ValueError("Stockholders Equity is zero, cannot calculate debt-to-equity ratio")

        result = float("{:.2f}".format(debt / equity))
        return result

    except (ValueError, TypeError) as e:
        return "N/A"
    
def debt_to_earnings(balance, income):
    latest_date = balance.columns.max()
    latest_balance = balance[latest_date]
    latest_income = income[latest_date]

    debt = latest_balance.get('Total Debt', None)
    earnings = latest_income.get('Gross Profit', None)

    if debt is None:
        debt = latest_balance.get('Total Liabilities Net Minority Interest', 'N/A')
    
    if earnings is None:
        earnings = latest_income.get('Pretax Income', 'N/A')

    try:
        debt = float(debt)
        earnings = float(earnings)

        if earnings == 0:
            raise ValueError("Earnings are zero, cannot calculate debt-to-earnings ratio")
        
        result = float("{:.2f}".format(debt / earnings))
        return result

    except (ValueError, TypeError) as e:
        return "N/A"
    
def earnings_yield(info):
    try:
        earnings_per_share = info.get('trailingEps', 'NaN')
        current_price = info.get('currentPrice', 'NaN')

        result = float("{:.2f}".format(earnings_per_share / current_price))

        return result

    except (ValueError, TypeError) as e:
        return "N/A"
    
def revenue_growth(income):
    latest_date = income.columns.max()
    oldest_date = income.columns.min()
    latest_income = income[latest_date]
    oldest_income = income[oldest_date]
    years = len(income.columns)

    latest_rev = latest_income.get('Total Revenue', 'NaN')
    oldest_rev = oldest_income.get('Total Revenue', 'NaN')

    change = ((latest_rev - oldest_rev) / oldest_rev) * 100
    avg_change = change / years

    return f"{avg_change:.2f}%"

def profit_margin(income):
    try:
        latest_date = income.columns.max()
        latest_income = income[latest_date]

        net_income = latest_income.get('Net Income', 'NaN')
        total_rev = latest_income.get('Total Revenue', 'NaN')

        if total_rev == 0:
            raise ValueError("Revenue is zero, cannot calculate profit margin")
        
        margin = (net_income / total_rev) * 100

        return f"{margin:.2f}%"

    except (ValueError, TypeError) as e:
        return "N/A"

def return_on_equity(balance, income):
    try:
        latest_date = balance.columns.max()
        latest_balance = balance[latest_date]
        latest_income = income[latest_date]

        net_income = latest_income.get('Net Income', 'NaN')
        equity = latest_balance.get('Stockholders Equity', 'NaN')

        if equity == 0:
            raise ValueError("Stockholders Equity is zero, cannot calculate debt-to-equity ratio")
        
        roe = (net_income / equity) * 100

        return f"{roe:.2f}%"
        
    except (ValueError, TypeError) as e:
        return "N/A"
    
def avg_free_cash_flow(cashflow):
    try:
        latest_date = cashflow.columns.max()
        oldest_date = cashflow.columns.min()
        latest_cashflow = cashflow[latest_date]
        oldest_cashflow = cashflow[oldest_date]
        years = len(cashflow.columns)
        flow = cashflow.loc['Free Cash Flow'].sort_index(ascending=False)
    
    except (ValueError, TypeError) as e:
        return "NaN"
    
def avg_free_cash_flow_change(cashflow):
    try:
        latest_date = cashflow.columns.max()
        oldest_date = cashflow.columns.min()
        latest_cashflow = cashflow[latest_date]
        oldest_cashflow = cashflow[oldest_date]
        years = len(cashflow.columns)

        latest_fcf = latest_cashflow.get('Free Cash Flow', 'NaN')
        oldest_fcf = oldest_cashflow.get('Free Cash Flow', 'NaN')

        change = ((latest_fcf - oldest_fcf) / oldest_fcf) * 100
        avg_change = change / years

        #return latest_fcf

        return f"{avg_change:.2f}%"

    except (ValueError, TypeError) as e:
        return "NaN"
    
def fcf_yield(cap, cash):
    try:
        cap = float(cap)
        cash = float(cash)

        if cap <= 0:
            raise ValueError("Market Capitalization should be greater than zero.")

        fcf_yield = (cash / cap) * 100
        return f"{fcf_yield:.2f}%"

    except ValueError as e:
        return f"Error: {e}"    

# def colorize(value, condition, low_threshold, high_threshold, use_color):
#     if not use_color:
#         return str(value)

#     # Check if the value is a percentage and remove the percentage sign
#     is_percentage = isinstance(value, str) and value.endswith('%')
#     value_float = float(value.rstrip('%')) if is_percentage else float(value)

#     if condition == "high":
#         if value_float > high_threshold:
#             color = '\033[92m'  # Green
#         elif low_threshold <= value_float <= high_threshold:
#             color = '\033[93m'  # Yellow
#         else:
#             color = '\033[91m'  # Red
#     elif condition == "low":
#         if value_float > high_threshold:
#             color = '\033[91m'  # Red
#         elif low_threshold <= value_float <= high_threshold:
#             color = '\033[93m'  # Yellow
#         else:
#             color = '\033[92m'  # Green
#     else:
#         color = '\033[0m'  # Default color

#     formatted_value = f"{value:.2f}" if isinstance(value, (float, int)) else str(value)

#     # Reset color to default after printing
#     reset_color = '\033[0m'

#     return f"{color}{formatted_value}{reset_color}"

def colorize(value, condition, low_threshold, high_threshold, use_color):
    if not use_color:
        return str(value)

    # Convert value to string
    value_str = str(value)

    # Check if the last character is NOT a digit
    suffix = value_str[-1] if not value_str[-1].isdigit() else None
    value_str = value_str[:-1] if suffix else value_str

    value_float = float(value_str)

    if condition == "high":
        if value_float > high_threshold:
            color = '\033[92m'  # Green
        elif low_threshold <= value_float <= high_threshold:
            color = '\033[93m'  # Yellow
        else:
            color = '\033[91m'  # Red
    elif condition == "low":
        if value_float > high_threshold:
            color = '\033[91m'  # Red
        elif low_threshold <= value_float <= high_threshold:
            color = '\033[93m'  # Yellow
        else:
            color = '\033[92m'  # Green
    else:
        color = '\033[0m'  # Default color

    formatted_value = f"{value_float:.2f}"

    # Reset color to default after printing
    reset_color = '\033[0m'

    # Include suffix if it exists
    return f"{color}{formatted_value}{suffix}{reset_color}" if suffix else f"{color}{formatted_value}{reset_color}"

def extract_numeric_value(value):
    if isinstance(value, str):
        # Remove percentage sign and currency suffix
        value = value.rstrip('%').rstrip('M').rstrip('B').rstrip('T').rstrip('Q').rstrip('K')

    try:
        return float(value)
    except ValueError:
        return None
    
def score_metric(value, thresholds):
    for threshold, score in thresholds:
        if value > threshold:
            return score
    return 0

def calc_score(ticker, table):
    try:
        _score = 0
        debt_to_equity = float(table["Debt to Equity"])
        debt_to_earnings = float(table["Debt to Earnings"])
        earnings_yield = float(table["Earnings Yield"])
        current_ratio = float(table["Current Ratio"])
        quick_ratio = float(table["Quick Ratio"])
        avg_revenue_growth = extract_numeric_value(table["Avg Revenue Growth"])
        profit_margin = extract_numeric_value(table["Profit Margin"])
        return_on_equity = extract_numeric_value(table["Return on Equity"])
        avg_cashflow_growth = extract_numeric_value(table["Avg Cashflow Growth"])
        cashflow_yield = extract_numeric_value(table["Cashflow Yield"])

        _score += score_metric(debt_to_equity, [(0.25, 3), (0.5, 2), (1, 1)])
        _score += score_metric(debt_to_earnings, [(0.25, 5), (0.5, 2), (1, 1)])
        _score += score_metric(earnings_yield, [(1, 3), (0.5, 2), (0, 1)])
        _score += score_metric(current_ratio, [(2, 3), (1, 2), (0.5, 1)])
        _score += score_metric(quick_ratio, [(2, 3), (1, 2), (0.5, 1)])
        _score += score_metric(avg_revenue_growth, [(30, 5), (15, 3), (10, 2), (5, 1)])
        _score += score_metric(profit_margin, [(30, 5), (15, 3), (10, 2), (5, 1)])
        _score += score_metric(return_on_equity, [(30, 5), (15, 3), (10, 2), (5, 1)])
        _score += score_metric(avg_cashflow_growth, [(30, 5), (15, 3), (10, 2), (5, 1)])
        _score += score_metric(cashflow_yield, [(10, 5), (5, 3), (3, 2), (1, 1)])

        return _score

    except (ValueError, TypeError) as e:
        return f"Failed to score {ticker}"

def remove_color(value):
    # Check if the value is a string
    if isinstance(value, str):
        # Remove ANSI escape codes (color codes) using a regular expression
        ansi_escape = re.compile(r'\033\[[0-9;]*[mG]')
        return ansi_escape.sub('', value)
    else:
        # If not a string, return the value unchanged
        return value

def remove_colors_from_table(table):
    # Create a new dictionary with colors removed from values
    cleaned_table = {key: remove_color(value) for key, value in table.items()}
    return cleaned_table

# def calc_score(ticker, table):
#     try:
#         debt_to_equity = table["Debt to Equity"]
#         debt_to_earnings = table["Debt to Earnings"]
#         earnings_yield = table["Earnings Yield"]
#         current_ratio = table["Current Ratio"]
#         quick_ratio = table["Quick Ratio"]
#         avg_revenue_growth = extract_numeric_value(table["Avg Revenue Growth"])
#         profit_margin = extract_numeric_value(table["Profit Margin"])
#         return_on_equity = extract_numeric_value(table["Return on Equity"])
#         avg_cashflow_growth = table["Avg Cashflow Growth"]
#         cashflow_yield = extract_numeric_value(table["Cashflow Yield"])
#         _score = 0

#         if debt_to_equity < 0.25:
#             _score += 3
#         elif debt_to_equity < 0.5:
#             _score += 2
#         elif debt_to_equity < 1:
#             _score += 1

#         if debt_to_earnings < 0.25:
#             _score += 5
#         elif debt_to_earnings < 0.5:
#             _score += 2
#         elif debt_to_earnings < 1:
#             _score += 1

#         if earnings_yield > 1:
#             _score += 3
#         elif earnings_yield > 0.5:
#             _score += 2
#         elif earnings_yield > 0:
#             _score += 1

#         if current_ratio > 2:
#             _score += 3
#         elif current_ratio > 1:
#             _score += 2
#         elif current_ratio > 0.5:
#             _score += 1

#         if quick_ratio > 2:
#             _score += 3
#         elif quick_ratio > 1:
#             _score += 2
#         elif quick_ratio > 0.5:
#             _score += 1

#         if avg_revenue_growth > 30:
#             _score += 5
#         elif avg_revenue_growth > 15:
#             _score += 3
#         elif avg_revenue_growth > 10:
#             _score += 2
#         elif avg_revenue_growth > 5:
#             _score += 1

#         if profit_margin > 30:
#             _score += 5
#         elif profit_margin > 15:
#             _score += 3
#         elif profit_margin > 10:
#             _score += 2
#         elif profit_margin > 5:
#             _score += 1
        
#         if return_on_equity > 30:
#             _score += 5
#         elif return_on_equity > 15:
#             _score += 3
#         elif return_on_equity > 10:
#             _score += 2
#         elif return_on_equity > 5:
#             _score += 1

#         if avg_cashflow_growth > 30:
#             _score += 5
#         elif avg_cashflow_growth > 15:
#             _score += 3
#         elif avg_cashflow_growth > 10:
#             _score += 2
#         elif avg_cashflow_growth > 5:
#             _score += 1

#         if cashflow_yield > 10:
#             _score += 5
#         elif avg_cashflow_growth > 5:
#             _score += 3
#         elif avg_cashflow_growth > 3:
#             _score += 2
#         elif avg_cashflow_growth > 1:
#             _score += 1

#         return _score

#     except (ValueError, TypeError) as e:
#         return f"Failed to score {ticker}"
