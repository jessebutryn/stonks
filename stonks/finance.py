import stonks.numbers as num

def debt_to_equity(balance):
    # Calculate the debt to equity ratio by dividing total debt by stockholder's equity
    latest_date = balance.columns.max()
    latest_balance = balance[latest_date]
    
    debt = latest_balance.get('Total Debt', None)
    equity = latest_balance.get('Stockholders Equity', 'NaN')

    # In the event there is no "Total Debt" metric for the given company we will try
    # to use 'Total Liabilities Net Minority Interest' instead.
    if debt is None:
        return latest_balance.get('Total Liabilities Net Minority Interest', 'NaN')

    try:
        debt = float(debt)
        equity = float(equity)

        if equity == 0:
            return "NaN"

        result = float("{:.2f}".format(debt / equity))
        return result

    except (ValueError, TypeError) as e:
        return "NaN"
    
def debt_to_earnings(balance, income):
    # Calculate the debt to earnings ratio by dividing total debt by gross profit.
    latest_date = balance.columns.max()
    latest_balance = balance[latest_date]
    latest_income = income[latest_date]

    debt = latest_balance.get('Total Debt', None)
    earnings = latest_income.get('Gross Profit', None)

    # In the event there is no "Total Debt" metric for the given company we will try
    # to use "Total Liabilities Net Minority Interest" instead.
    if debt is None:
        debt = latest_balance.get('Total Liabilities Net Minority Interest', 'NaN')
    
    # In the event there is no "Gross Profit" metric for the given company we will try
    # to use "Pretax Income" instead.
    if earnings is None:
        earnings = latest_income.get('Pretax Income', 'NaN')

    try:
        debt = float(debt)
        earnings = float(earnings)

        if earnings == 0:
            return "NaN"
        
        result = float("{:.2f}".format(debt / earnings))
        return result

    except (ValueError, TypeError) as e:
        return "NaN"
    
def earnings_yield(info):
    # Calculate earnings yield by diving earnings per share by the current share price
    try:
        earnings_per_share = info.get('trailingEps', 'NaN')
        current_price = info.get('currentPrice', 'NaN')

        result = float("{:.2f}".format(earnings_per_share / current_price))

        return result

    except (ValueError, TypeError) as e:
        return "NaN"
    
def revenue_growth(income):
    # Calculate percentage of growth from the oldest revenue number returned
    # (typically 4 years) to the newest revenue number returned.
    latest_date = income.columns.max()
    oldest_date = income.columns.min()
    latest_income = income[latest_date]
    oldest_income = income[oldest_date]
    years = len(income.columns)

    latest_rev = latest_income.get('Total Revenue', 'NaN')
    oldest_rev = oldest_income.get('Total Revenue', 'NaN')

    if oldest_rev == 0 or oldest_rev == 'NaN':
        return "NaN"

    change = ((latest_rev - oldest_rev) / oldest_rev) * 100
    avg_change = change / years

    return f"{avg_change:.2f}%"


def profit_margin(income):
    # Calculate the profit margin by dividing "Net Income" by "Total Revenue"
    try:
        latest_date = income.columns.max()
        latest_income = income[latest_date]

        net_income = latest_income.get('Net Income', 'NaN')
        total_rev = latest_income.get('Total Revenue', 'NaN')

        if total_rev == 0:
            return "NaN"
        
        margin = (net_income / total_rev) * 100

        return f"{margin:.2f}%"

    except (ValueError, TypeError) as e:
        return "NaN"

def return_on_equity(balance, income):
    # Calculate return on equity by dividing "Net Income" by the
    # "Stockholders Equity"
    try:
        latest_date = balance.columns.max()
        latest_balance = balance[latest_date]
        latest_income = income[latest_date]

        net_income = latest_income.get('Net Income', 'NaN')
        equity = latest_balance.get('Stockholders Equity', 'NaN')

        if equity == 0:
            return "NaN"
        
        roe = (net_income / equity) * 100

        return f"{roe:.2f}%"
        
    except (ValueError, TypeError) as e:
        return "NaN"
    
def avg_free_cash_flow_change(cashflow):
    # Calculate average free cash flow change year over year from oldest
    # data returned (typically 4 years) to latest year returned.
    try:
        latest_date = cashflow.columns.max()
        oldest_date = cashflow.columns.min()
        latest_cashflow = cashflow[latest_date]
        oldest_cashflow = cashflow[oldest_date]
        years = len(cashflow.columns)

        latest_fcf = latest_cashflow.get('Free Cash Flow', 'NaN')
        oldest_fcf = oldest_cashflow.get('Free Cash Flow', 'NaN')

        if oldest_fcf == 0 or oldest_fcf == 'NaN':
            return "NaN"

        change = ((latest_fcf - oldest_fcf) / oldest_fcf) * 100
        avg_change = change / years

        return f"{avg_change:.2f}%"

    except (ValueError, TypeError) as e:
        return "NaN"
    
def fcf_yield(cap, cash):
    # Calculate the free cash flow yield by dividing free cash flow by
    # the current market cap.  In my opinion this is possible the most
    # important metric when looking at a business.  How much does it cost
    # and how much cash will it put in my pocket?
    try:
        cap = float(cap)
        cash = float(cash)

        if cap <= 0:
            return "NaN"

        fcf_yield = (cash / cap) * 100
        return f"{fcf_yield:.2f}%"

    except ValueError as e:
        return f"Error: {e}"    

def calc_score(ticker, table):
    # This is probably an excessively rudimentary function to calculate the
    # "score" of the given business.  This is completely opinionated and even
    # somewhat arbitrary.  I'm not sure what the actual threshold for a "good"
    # score is but the "perfect" score is 42.  Life, the universe, and everything.
    try:
        debt_to_equity = float(table.get("Debt to Equity", 2))
        debt_to_earnings = float(table.get("Debt to Earnings", 2))
        earnings_yield = float(table.get("Earnings Yield", 0))
        current_ratio = float(table.get("Current Ratio", 0))
        quick_ratio = float(table.get("Quick Ratio", 0))
        avg_revenue_growth = num.extract_numeric_value(table.get("Avg Revenue Growth", 0))
        profit_margin = num.extract_numeric_value(table.get("Profit Margin", 0))
        return_on_equity = num.extract_numeric_value(table.get("Return on Equity", 0))
        avg_cashflow_growth = num.extract_numeric_value(table.get("Avg Cashflow Growth", 0))
        cashflow_yield = num.extract_numeric_value(table.get("Cashflow Yield", 0))
        _score = 0

        # The best debt is no debt but the lower the better.
        if debt_to_equity < 0.25:
            _score += 3
        elif debt_to_equity < 0.5:
            _score += 2
        elif debt_to_equity < 1:
            _score += 1

        # The best debt is no debt but the lower the better.
        if debt_to_earnings < 0.25:
            _score += 5
        elif debt_to_earnings < 0.5:
            _score += 2
        elif debt_to_earnings < 1:
            _score += 1

        # Higher earnings are rewarded.  This may need to be adjusted as
        # it is extremely unlikely a company will ever have greater earnings
        # than cost.  And if that were to happen it would likely mean some new
        # information about the company indicates future prospects are very much
        # different than past.
        if earnings_yield > 1:
            _score += 3
        elif earnings_yield > 0.5:
            _score += 2
        elif earnings_yield > 0:
            _score += 1

        # Current ratio is the ratio of all assets to all liabilities.  Since
        # almost all companies engage in very creative accounting tactics I
        # don't trust this metric alone which is why I added debt to equity and
        # debt to earnings metrics. 
        #
        # Still we like to see more assets than liabilities.
        if current_ratio > 2:
            _score += 3
        elif current_ratio > 1:
            _score += 2
        elif current_ratio > 0.5:
            _score += 1

        # Quick ratio (or Acid test ratio) is a bit better than the current ratio
        # as it only accounts for liquid assets vs liabilities.
        if quick_ratio > 2:
            _score += 3
        elif quick_ratio > 1:
            _score += 2
        elif quick_ratio > 0.5:
            _score += 1

        # The faster a company grows revenue the better.
        if avg_revenue_growth > 30:
            _score += 5
        elif avg_revenue_growth > 15:
            _score += 3
        elif avg_revenue_growth > 10:
            _score += 2
        elif avg_revenue_growth > 5:
            _score += 1

        # Higher profit margins are better
        if profit_margin > 30:
            _score += 5
        elif profit_margin > 15:
            _score += 3
        elif profit_margin > 10:
            _score += 2
        elif profit_margin > 5:
            _score += 1
        
        # Higher return on equity is better
        if return_on_equity > 30:
            _score += 5
        elif return_on_equity > 15:
            _score += 3
        elif return_on_equity > 10:
            _score += 2
        elif return_on_equity > 5:
            _score += 1

        # Growing cashflow is better
        if avg_cashflow_growth > 30:
            _score += 5
        elif avg_cashflow_growth > 15:
            _score += 3
        elif avg_cashflow_growth > 10:
            _score += 2
        elif avg_cashflow_growth > 5:
            _score += 1

        # Cashflow yield, again, is my favorite metric for a business. This
        # number tells you what you get for your dollar.  You can't accurately
        # predict the future prospects of a company but this number tells you
        # what kind of return the business presently makes.
        if cashflow_yield > 10:
            _score += 5
        elif avg_cashflow_growth > 5:
            _score += 3
        elif avg_cashflow_growth > 3:
            _score += 2
        elif avg_cashflow_growth > 1:
            _score += 1

        return _score

    except (ValueError, TypeError) as e:
        return f"Failed to score {ticker}"
