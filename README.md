# Stonks

Stonks is a Python project that leverages the Yahoo Finance API through `yfinance` to gather company stock and financial information. This repository provides scripts for retrieving data and generating various reports on the financial health of companies.

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)

## Introduction

Stonks is a project designed to provide a streamlined and focused overview of key financial metrics for companies you care about. The primary goal is to quickly deliver essential insights into specific financial indicators such as debt, revenue growth, and free cash flow. While recognizing that past performance analysis cannot predict a company's future success, the emphasis here is on avoiding investments in companies with insufficient income and unmanageable debt. Stonks aims to empower users with a concise yet comprehensive snapshot of essential financial data, aiding in informed decision-making when considering potential investments.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/stonks.git && cd stonks
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Install package:

    ```bash
    pip install -e .
    ```

4. Alternatively:

    If you don't want to install the module you can just run it from within the repository dir like so:
    
    ```bash
    python3 stonks --help
    ```

## Usage

1. Help

    ```bash
    $ stonks --help
    usage: stonks [-h] [--no-color] [--summarize] [--score] [--csv] [-H] ticker

    Stonks as hell

    positional arguments:
    ticker        Stock ticker symbol

    optional arguments:
    -h, --help    show this help message and exit
    --no-color    Disable colored output
    --summarize   Run summarize commands
    --score       Run score commands
    --csv         Output in CSV format
    -H, --header  Include header in CSV output
    ```

1. Example

    ```bash
    $ stonks msft --summarize
    Attribute            Value
    -------------------  -------
    Market Cap           2.78T
    Current Price        374.58
    Debt to Equity       0.29
    Debt to Earnings     0.41
    Earnings Yield       0.03
    Current Ratio        1.66
    Quick Ratio          1.53
    Avg Revenue Growth   12.04%
    Profit Margin        34.15%
    Return on Equity     35.09%
    EPS                  10.34
    PE                   36.23
    Avg Cashflow         56.49B
    Avg Cashflow Growth  7.87%
    Cashflow Yield       2.03%
    Score                25.00
    ```

## Uninstall

```bash
pip uninstall stonks
```
