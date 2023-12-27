import stonks.numbers as num

def debt_to_equity(data):
    # Calculate the debt to equity ratio by dividing total debt by stockholder's equity

    qbalance = data['quarterly_balance_sheet']

    if qbalance.empty:
        return None
    
    latest_date = qbalance.columns.max()
    latest_balance = qbalance[latest_date]
    
    debt = latest_balance.get('Total Debt', None)
    equity = latest_balance.get('Stockholders Equity', None)

    # In the event there is no "Total Debt" metric for the given company we will try
    # to use 'Total Liabilities Net Minority Interest' instead.
    if debt is None or str(debt).lower() == 'nan':
        debt = latest_balance.get('Total Liabilities Net Minority Interest', 'NaN')

    try:
        debt = float(debt)
        equity = float(equity)

        if equity == 0:
            return "NaN"

        result = float("{:.2f}".format(debt / equity))
        return result

    except (ValueError, TypeError) as e:
        return 'NaN'
    
def debt_to_earnings(data):
    # Calculate the debt to earnings ratio by dividing total debt by gross profit.

    qbalance = data['quarterly_balance_sheet']
    qincome = data['quarterly_income_stmt']

    if qbalance.empty or qincome.empty:
        return None
    
    latest_b_date = qbalance.columns.max()
    latest_i_date = qincome.columns.max()
    latest_balance = qbalance[latest_b_date]
    latest_income = qincome[latest_i_date]

    debt = latest_balance.get('Total Debt', None)
    earnings = latest_income.get('Gross Profit', None)

    # In the event there is no "Total Debt" metric for the given company we will try
    # to use "Total Liabilities Net Minority Interest" instead.
    if debt is None or str(debt).lower() == 'nan':
        debt = latest_balance.get('Total Liabilities Net Minority Interest', None)
    
    # In the event there is no "Gross Profit" metric for the given company we will try
    # to use "Pretax Income" instead.
    if earnings is None or str(earnings).lower() == 'nan':
        earnings = latest_income.get('Pretax Income', None)

    try:
        debt = float(debt)
        earnings = float(earnings)

        if earnings == 0:
            return "NaN"
        
        result = float("{:.2f}".format(debt / earnings))
        return result

    except (ValueError, TypeError) as e:
        return 'NaN'
    
def earnings_yield(data):
    # Calculate earnings yield by diving earnings per share by the current share price
    try:
        earnings_per_share = data['info'].get('trailingEps', None)
        current_price = data['info'].get('currentPrice', None)

        result = float("{:.2f}".format(earnings_per_share / current_price))

        return result

    except (ValueError, TypeError) as e:
        return "NaN"
    
def revenue_growth(data):
    # Calculate percentage of growth from the oldest revenue number returned
    # (typically 4 years) to the newest revenue number returned.
    try:
        income = data['income_stmt']

        if income.empty or 'Total Revenue' not in income.index:
            return None
        
        value = income.loc['Total Revenue'].dropna()

        if value.empty or value.isna().all():
            return None
        
        latest_rev = value[value.index == value.index.max()].values[0]
        oldest_rev = value[value.index == value.index.min()].values[0]
        years = value.index.nunique()
        
        if oldest_rev == 0 or oldest_rev == 'NaN':
            return "NaN"

        change = ((latest_rev - oldest_rev) / oldest_rev) * 100
        avg_change = change / years

        return f"{avg_change:.2f}%"
    
    except (ValueError, TypeError) as e:
        return 'NaN'


def profit_margin(data):
    # Calculate the profit margin by dividing "Net Income" by "Total Revenue"
    try:
        income = data['income_stmt']

        if income.empty:
            return None
        
        latest_date = income.columns.max()
        latest_income = income[latest_date]

        net_income = latest_income.get('Net Income', None)
        total_rev = latest_income.get('Total Revenue', None)

        if total_rev == 0:
            return "NaN"
        
        margin = (net_income / total_rev) * 100

        return f"{margin:.2f}%"

    except (ValueError, TypeError) as e:
        return 'NaN'

def return_on_equity(data):
    # Calculate return on equity by dividing "Net Income" by the
    # "Stockholders Equity"
    try:
        balance = data['balance_sheet']
        income = data['income_stmt']

        if income.empty or balance.empty:
            return None
    
        latest_b_date = balance.columns.max()
        latest_i_date = income.columns.max()
        latest_balance = balance[latest_b_date]
        latest_income = income[latest_i_date]

        net_income = latest_income.get('Net Income', None)
        equity = latest_balance.get('Stockholders Equity', None)

        if equity == 0:
            return "NaN"
        
        roe = (net_income / equity) * 100

        return f"{roe:.2f}%"
        
    except (ValueError, TypeError) as e:
        return 'NaN'
    
def avg_free_cash_flow_change(data):
    # Calculate average free cash flow change year over year from oldest
    # data returned (typically 4 years) to latest year returned.
    try:
        cashflow = data['cashflow']

        if cashflow.empty:
            return None
        
        value = cashflow.loc['Free Cash Flow'].dropna()
        latest_fcf = value[value.index == value.index.max()].values[0]
        oldest_fcf = value[value.index == value.index.min()].values[0]
        years = value.index.nunique()

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

    except (ValueError, TypeError) as e:
        return 'NaN'
    
def current_ratio(data):
    # Calculate current ratio
    try:
        ratio = data['info'].get('currentRatio', None)
        wing_it = None

        if ratio is not None:
            return ratio
        else:
            wing_it = True

        qbalance = data['quarterly_balance_sheet']

        if qbalance.empty:
            return None
        
        latest_date = qbalance.columns.max()
        latest_balance = qbalance[latest_date]

        current_liabilities = latest_balance.get('Current Liabilities', None)
        current_assets = latest_balance.get('Current Assets', None)

        if current_liabilities is None:
            accounts_payable = latest_balance.get('Payables And Accrued Expenses', 0)
            deferred_liabilities = latest_balance.get('Current Deferred Liabilities', 0)
            current_debt = latest_balance.get('Current Debt', 0)
            other = latest_balance.get('Other Current Liabilities', 0)
            current_liabilities = accounts_payable + deferred_liabilities + current_debt + other

        if current_assets is None:
            cash = latest_balance.get('Cash Cash Equivalents And Short Term Investments', 0)
            receivables = latest_balance.get('Receivables', 0)
            inventory = latest_balance.get('Inventory', 0)
            current_assets = cash + receivables + inventory

        if current_liabilities == 0 or current_liabilities is None:
            return 'NaN'
        
        ratio = current_assets / current_liabilities

        if wing_it:
            return f"{ratio:.2f}*"
        
        return f"{ratio:.2f}"

    except ValueError as e:
        return 'NaN'
    
def quick_ratio(data):
    # Calculate the quick ratio
    try:
        ratio = data['info'].get('quickRatio', None)
        wing_it = None

        if ratio is not None:
            return ratio
        else:
            wing_it = True

        qbalance = data['quarterly_balance_sheet']

        if qbalance.empty:
            return None
        
        latest_date = qbalance.columns.max()
        latest_balance = qbalance[latest_date]

        current_liabilities = latest_balance.get('Current Liabilities', None)
        cash = latest_balance.get('Cash Cash Equivalents And Short Term Investments', 0)
        receivables = latest_balance.get('Receivables', 0)
        current_assets = cash + receivables

        if current_liabilities is None:
            accounts_payable = latest_balance.get('Payables And Accrued Expenses', 0)
            deferred_liabilities = latest_balance.get('Current Deferred Liabilities', 0)
            current_debt = latest_balance.get('Current Debt', 0)
            other = latest_balance.get('Other Current Liabilities', 0)
            current_liabilities = accounts_payable + deferred_liabilities + current_debt + other

        if current_liabilities == 0 or current_liabilities is None:
            return 'NaN'
        
        ratio = current_assets / current_liabilities

        if wing_it:
            return f"{ratio:.2f}*"
        
        return f"{ratio:.2f}"

    except ValueError as e:
        return 'NaN'
    
def avg_free_cash_flow(data):
    try:
        _raw_fcf = data['cashflow'].loc['Free Cash Flow'].dropna().sort_index(ascending=False).mean()
        return _raw_fcf
    except (KeyError, AttributeError, TypeError):
        return None

def calc_score(table):
    # This is probably an excessively rudimentary function to calculate the
    # "score" of the given business.  This is completely opinionated and even
    # somewhat arbitrary.  I'm not sure what the actual threshold for a "good"
    # score is but the "perfect" score is 42.  Life, the universe, and everything.
    try:
        ticker = table.get("Ticker")
        debt_to_equity = num.extract_numeric_value(table.get("Debt to Equity"), 2)
        debt_to_earnings = num.extract_numeric_value(table.get("Debt to Earnings"), 2)
        earnings_yield = num.extract_numeric_value(table.get("Earnings Yield"), 2)
        current_ratio = num.extract_numeric_value(table.get("Current Ratio"), 2)
        quick_ratio = num.extract_numeric_value(table.get("Quick Ratio"), 2)
        avg_revenue_growth = num.extract_numeric_value(table.get("Avg Revenue Growth"), 2)
        profit_margin = num.extract_numeric_value(table.get("Profit Margin"), 2)
        return_on_equity = num.extract_numeric_value(table.get("Return on Equity"), 2)
        avg_cashflow_growth = num.extract_numeric_value(table.get("Avg Cashflow Growth"), 2)
        cashflow_yield = num.extract_numeric_value(table.get("Cashflow Yield"), 2)
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
        return f"Failed to score {ticker}: {e}"
