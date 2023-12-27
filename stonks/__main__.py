#!/usr/bin/env python3
import yfinance as yf
import sys
import csv
import json
from tabulate import tabulate
import pandas as pd
import argparse
import time
import stonks.numbers as num
import stonks.finance as fin
import stonks.formatting as fmt
import stonks.info as info

def make_table(ticker, use_color, data):
    """
    Build a table with financial metrics for a given stock ticker.

    Parameters:
    - ticker (str): Stock ticker symbol.
    - use_color (bool): Flag to enable or disable color formatting.
    - info: Information about the stock.
    - balance: Balance sheet data.
    - income: Income statement data.
    - cashflow: Cashflow data.

    Returns:
    dict: A dictionary representing the financial metrics table.
    """

    _raw_cap = data['info'].get('marketCap', None)
    _mkt_cap = num.format_currency(_raw_cap)
    _current_price = num.format_currency(data['info'].get('currentPrice', None))
    _debt_to_equity = fin.debt_to_equity(data)
    _debt_to_equity = fmt.colorize(_debt_to_equity, "low", 0.5, 1, use_color)
    _debt_to_earnings = fin.debt_to_earnings(data)
    _debt_to_earnings = fmt.colorize(_debt_to_earnings, "low", 1, 2, use_color)
    _earnings_yield = fin.earnings_yield(data)
    _earnings_yield = fmt.colorize(_earnings_yield, "high", 1, 2, use_color)
    _current_ratio = fin.current_ratio(data)
    _current_ratio = fmt.colorize(_current_ratio, "high", 1, 1, use_color)
    _quick_ratio = fin.quick_ratio(data)
    _quick_ratio = fmt.colorize(_quick_ratio, "high", 1, 1, use_color)
    _avg_revenue_growth = fin.revenue_growth(data)
    _avg_revenue_growth = fmt.colorize(_avg_revenue_growth, "high", 8, 12, use_color)
    _profit_margin = fin.profit_margin(data)
    _profit_margin = fmt.colorize(_profit_margin, "high", 10, 15, use_color)
    _roe = fin.return_on_equity(data)
    _roe = fmt.colorize(_roe, "high", 10, 15, use_color)
    _eps = data['info'].get('trailingEps', None)
    _eps = fmt.colorize(_eps, "high", 3, 8, use_color)
    _pe = round(float(data['info'].get('trailingPE', 'NaN')), 2)
    _avg_fcf_change = fin.avg_free_cash_flow_change(data)
    _avg_fcf_change = fmt.colorize(_avg_fcf_change, "high", 5, 10, use_color)
    _raw_fcf = fin.avg_free_cash_flow(data)
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
    _score = fin.calc_score(clean_table)
    _score = fmt.colorize(_score, "high", 20, 28, use_color)
    # Add score to orginal table
    table["Score"] = _score

    return table

def process_ticker(ticker, use_color, output, csv_writer, print_info, quarterly):
    """
    Process a single stock ticker and output financial metrics.

    Parameters:
    - ticker (str): Stock ticker symbol.
    - use_color (bool): Flag to enable or disable color formatting.
    - output_csv (bool): Flag to determine the output format (CSV or table).
    - csv_writer: CSV writer object for writing to stdout.
    """
    try:
        ticker = ticker.replace('/', '-').replace('.', '-')
        data_class = info.FinancialData(ticker)
        data = data_class.data

        if print_info is not None:
            pdata = info.print_data(data, print_info, quarterly)
            print(pdata)
        else:
            # We don't want color formatting data mucking up csv output
            if output is not None:
                use_color = False

            table = make_table(ticker, use_color, data)

            # Output data in either csv or table format depending on what is requested
            if output == 'csv':
                csv_writer.writerow([str(value) for value in table.values()])
            elif output == 'json':
                json_string = json.dumps(table, indent=2)
                print(json_string)        
            else:
                table_as_list = [[key, value] for key, value in table.items()]
                print(tabulate(table_as_list, headers=["Attribute", "Value"], tablefmt="simple"))

    except (ValueError, TypeError) as e:
        return f"{ticker} Error: {e}"
        
def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Stonks - A financial analysis tool for stock tickers, providing key metrics and scores for informed investment decisions.')
    parser.add_argument('tickers', nargs='*', type=str, help='Stock ticker symbols')
    parser.add_argument('-f', '--file', type=str, help='Read ticker symbols from a file')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--csv', action='store_true', help='Output in CSV format') 
    parser.add_argument('-H', '--header', action='store_true', help='Include header in CSV output')
    parser.add_argument('--json', action='store_true', help='Output in json format')
    parser.add_argument('--info', choices=['info', 'balance', 'income', 'cashflow', 'financials'], help='Specify the type of financial information to retrieve')
    parser.add_argument('-q', '--quarterly', action='store_true', help='When used with --info this will return quarterly results instead of annual')

    args = parser.parse_args()

    use_color = not args.no_color
    output_csv = args.csv
    output_json = args.json
    use_header = args.header
    print_info = args.info
    quarterly = args.quarterly
    tickers = []

    if output_csv:
        output = 'csv'
    elif output_json:
        output = 'json'
    else:
        output = None

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
    if output == 'csv' and use_header:
        csv_writer.writerow(["Ticker", "Market Cap", "Current Price", "Debt to Equity", "Debt to Earnings",
                            "Earnings Yield", "Current Ratio", "Quick Ratio", "Avg Revenue Growth",
                            "Profit Margin", "Return on Equity", "EPS", "PE", "Avg Cashflow",
                            "Avg Cashflow Growth", "Cashflow Yield", "Score"])

    # Run process_ticker() for each ticker in tickers.
    for ticker in tickers:
        process_ticker(ticker, use_color, output, csv_writer, print_info, quarterly)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
