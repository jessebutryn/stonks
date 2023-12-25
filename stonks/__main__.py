#!/usr/bin/env python3
import yfinance as yf
import sys
import csv
from tabulate import tabulate
import pandas as pd
import argparse
import stonks.numbers as num
import stonks.finance as fin
import stonks.formatting as fmt

def process_ticker(ticker, use_color, output_csv, csv_writer):
    # This function gathers all the information required for a single given ticker and outputs
    # in the desired format.

    # Gather the required info from yfinance
    data = yf.Ticker(ticker)
    info = data.info
    balance = data.balance_sheet
    income = data.income_stmt
    cashflow = data.cashflow

    # Check length of yfinance objects and exit if any are empty
    len_balance = len(balance.columns)
    len_income = len(income.columns)
    len_cashflow = len(cashflow.columns)

    if len_balance == 0 or len_income == 0 or len_cashflow == 0:
        print(f"Error: {ticker} not enough data")
        sys.exit(1)

    # We don't want color formatting data mucking up csv output
    if output_csv:
        use_color = False

    # Gather up all the desired metrics for our output.
    _raw_cap = info.get('marketCap', 'NaN')
    _mkt_cap = num.format_currency(_raw_cap)
    _current_price = num.format_currency(info.get('currentPrice', 'NaN'))
    _debt_to_equity = fin.debt_to_equity(balance)
    _debt_to_equity = fmt.colorize(_debt_to_equity, "low", 0.5, 1, use_color)
    _debt_to_earnings = fin.debt_to_earnings(balance, income)
    _debt_to_earnings = fmt.colorize(_debt_to_earnings, "low", 1, 2, use_color)
    _earnings_yield = fin.earnings_yield(info)
    _earnings_yield = fmt.colorize(_earnings_yield, "high", 1, 2, use_color)
    _current_ratio = info.get('currentRatio', 'NaN')
    _current_ratio = fmt.colorize(_current_ratio, "high", 1, 1, use_color)
    _quick_ratio = info.get('quickRatio', 'NaN')
    _quick_ratio = fmt.colorize(_quick_ratio, "high", 1, 1, use_color)
    _avg_revenue_growth = fin.revenue_growth(income)
    _avg_revenue_growth = fmt.colorize(_avg_revenue_growth, "high", 8, 12, use_color)
    _profit_margin = fin.profit_margin(income)
    _profit_margin = fmt.colorize(_profit_margin, "high", 10, 15, use_color)
    _roe = fin.return_on_equity(balance, income)
    _roe = fmt.colorize(_roe, "high", 10, 15, use_color)
    _eps = info.get('trailingEps', 'NaN')
    _eps = fmt.colorize(_eps, "high", 3, 8, use_color)
    _pe = round(float(info.get('trailingPE', 'NaN')), 2)
    _avg_fcf_change = fin.avg_free_cash_flow_change(cashflow)
    _avg_fcf_change = fmt.colorize(_avg_fcf_change, "high", 5, 10, use_color)
    _raw_fcf = cashflow.loc['Free Cash Flow'].sort_index(ascending=False).mean()
    _avg_fcf = num.format_currency(_raw_fcf)
    _avg_fcf = fmt.colorize(_avg_fcf, "high", 0, 1, use_color)
    _fcf_yield = fin.fcf_yield(_raw_cap, _raw_fcf)
    _fcf_yield = fmt.colorize(_fcf_yield, "high", 0, 5, use_color)

    # Build table with desired data
    table = {
        "Ticker": ticker.upper(),
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

    # We need a table with no colors in order to calculate the score
    clean_table = fmt.remove_colors_from_table(table)
    _score = fin.calc_score(ticker, clean_table)
    _score = fmt.colorize(_score, "high", 20, 28, use_color)
    # Add score to orginal table
    table["Score"] = _score
 
    # Output data in either csv or table format depending on what is requested
    if output_csv:
        csv_writer.writerow([str(value) for value in table.values()])
    else:
        table_as_list = [[key, value] for key, value in table.items()]
        print(tabulate(table_as_list, headers=["Attribute", "Value"], tablefmt="simple"))
    
def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Stonks - A financial analysis tool for stock tickers, providing key metrics and scores for informed investment decisions.')
    parser.add_argument('tickers', nargs='*', type=str, help='Stock ticker symbols')
    parser.add_argument('-f', '--file', type=str, help='Read ticker symbols from a file')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--csv', action='store_true', help='Output in CSV format') 
    parser.add_argument('-H', '--header', action='store_true', help='Include header in CSV output')

    args = parser.parse_args()

    use_color = not args.no_color
    output_csv = args.csv
    use_header = args.header
    tickers = []

    # read args from file 
    if args.file:
        with open(args.file, 'r') as file:
            tickers.extend(file.read().splitlines())
    else:
        tickers = args.tickers

    # errexit if no tickers are provided
    if not tickers:
        print("Error: No ticker symbols provided.")
        sys.exit(1)

    # define csv_writer
    csv_writer = csv.writer(sys.stdout)

    # I'm not a fan of how this works but if header is to be printed I only want it to be printed once so
    # this manually creates that header row before the process_ticker() iterations.
    if output_csv and use_header:
        csv_writer.writerow(["Ticker", "Market Cap", "Current Price", "Debt to Equity", "Debt to Earnings",
                            "Earnings Yield", "Current Ratio", "Quick Ratio", "Avg Revenue Growth",
                            "Profit Margin", "Return on Equity", "EPS", "PE", "Avg Cashflow",
                            "Avg Cashflow Growth", "Cashflow Yield", "Score"])

    # Run process_ticker() for each ticker in tickers.
    for ticker in tickers:
        process_ticker(ticker, use_color, output_csv, csv_writer)

if __name__ == "__main__":
    main()
