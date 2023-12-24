#!/usr/bin/env python3
import yfinance as yf
import sys
import csv
from tabulate import tabulate
import pandas as pd
import argparse
#from pprint import pprint
from functions import *

# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# use_color = True

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python financial_data.py <ticker>")
#         sys.exit(1)

#     ticker = sys.argv[1]
    
def main():
    parser = argparse.ArgumentParser(description='Stonks as hell')
    parser.add_argument('ticker', type=str, help='Stock ticker symbol')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--summarize', action='store_true', help='Run summarize commands')
    parser.add_argument('--score', action='store_true', help='Run score commands')
    parser.add_argument('--csv', action='store_true', help='Output in CSV format') 
    parser.add_argument('-H', '--header', action='store_true', help='Include header in CSV output')

    args = parser.parse_args()

    # Access the arguments
    ticker = args.ticker
    use_color = not args.no_color
    summarize = args.summarize
    score = args.score
    output_csv = args.csv
    use_header = args.header

    data = yf.Ticker(ticker)
    info = data.info
    balance = data.balance_sheet
    income = data.income_stmt
    cashflow = data.cashflow

    #len_info = len(info.columns)
    len_balance = len(balance.columns)
    len_income = len(income.columns)
    len_cashflow = len(cashflow.columns)

    if score or output_csv:
        use_color = False

    if len_balance == 0 or len_income == 0 or len_cashflow == 0:
        print(f"Error: {ticker} not enough data")
        sys.exit(1)


    _raw_cap = info.get('marketCap', 'NaN')
    _mkt_cap = format_currency(_raw_cap)
    _current_price = format_currency(info.get('currentPrice', 'NaN'))
    _debt_to_equity = debt_to_equity(balance)
    _debt_to_equity = colorize(_debt_to_equity, "low", 0.5, 1, use_color)
    _debt_to_earnings = debt_to_earnings(balance, income)
    _debt_to_earnings = colorize(_debt_to_earnings, "low", 1, 2, use_color)
    _earnings_yield = earnings_yield(info)
    _earnings_yield = colorize(_earnings_yield, "high", 1, 2, use_color)
    _current_ratio = info.get('currentRatio', 'NaN')
    _current_ratio = colorize(_current_ratio, "high", 1, 1, use_color)
    _quick_ratio = info.get('quickRatio', 'NaN')
    _quick_ratio = colorize(_quick_ratio, "high", 1, 1, use_color)
    _avg_revenue_growth = revenue_growth(income)
    _avg_revenue_growth = colorize(_avg_revenue_growth, "high", 8, 12, use_color)
    _profit_margin = profit_margin(income)
    _profit_margin = colorize(_profit_margin, "high", 10, 15, use_color)
    _roe = return_on_equity(balance, income)
    _roe = colorize(_roe, "high", 10, 15, use_color)
    _eps = info.get('trailingEps', 'NaN')
    _eps = colorize(_eps, "high", 3, 8, use_color)
    _pe = round(float(info.get('trailingPE', 'NaN')), 2)
    _avg_fcf_change = avg_free_cash_flow_change(cashflow)
    _avg_fcf_change = colorize(_avg_fcf_change, "high", 5, 10, use_color)
    _raw_fcf = cashflow.loc['Free Cash Flow'].sort_index(ascending=False).mean()
    _avg_fcf = format_currency(_raw_fcf)
    _avg_fcf = colorize(_avg_fcf, "high", 0, 1, use_color)
    _fcf_yield = fcf_yield(_raw_cap, _raw_fcf)
    _fcf_yield = colorize(_fcf_yield, "high", 0, 5, use_color)

    table = {
        "Market Cap": _mkt_cap,
        "Current Price": _current_price,
        "Debt to Equity": _debt_to_equity,
        "Debt to Earnings": _debt_to_earnings,
        "Earnings Yield": _earnings_yield,
        "Current Ratio": _current_ratio,
        "Quick Ratio": _quick_ratio,
        "Avg Revenue Growth": _avg_revenue_growth,
        "Profit Margin": _profit_margin,
        "Return on Equity": _roe,
        "EPS": _eps,
        "PE": _pe,
        "Avg Cashflow": _avg_fcf,
        "Avg Cashflow Growth": _avg_fcf_change,
        "Cashflow Yield": _fcf_yield,
    }

    clean_table = remove_colors_from_table(table)
    _score = calc_score(ticker, clean_table)
    _score = colorize(_score, "high", 15, 30, use_color)
    table["Score"] = _score

    if summarize:
        if output_csv:
            csv_writer = csv.writer(sys.stdout)
            if use_header:
                csv_writer.writerow(["Ticker"] + list(table.keys()))
            csv_writer.writerow([ticker] + [str(value) for value in table.values()])
        else:
            # Output as a table
            table_as_list = [[key, value] for key, value in table.items()]
            print(tabulate(table_as_list, headers=["Attribute", "Value"], tablefmt="simple"))
        # table_as_list = [[key, value] for key, value in table.items()]
        # print(tabulate(table_as_list, headers=["Attribute", "Value"], tablefmt="simple"))
    elif score:
        print(f"{ticker}:{_score}")
    else:
        print('No specific action specified.')

if __name__ == "__main__":
    main()
