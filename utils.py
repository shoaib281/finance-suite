import json

"""
company_tickers.json
https://www.sec.gov/file/company-tickers
"""

def ticker_to_cik(ticker):
    ticker = ticker.upper()

    with open("company_tickers_exchange.json") as file:
        d = json.load(file)["data"]

    for stock in d:
        if stock[2] == ticker:
            return stock[0]
