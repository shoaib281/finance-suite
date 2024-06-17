import json
import subprocess

"""
company_tickers.json
https://www.sec.gov/file/company-tickers
"""

def copy_to_clipboard(data):
    data = data.encode()
    p = subprocess.Popen(['xclip','-selection','clipboard'], stdin=subprocess.PIPE)
    p.stdin.write(data)
    p.stdin.close()
    retcode = p.wait()


def ticker_to_cik(ticker):
    ticker = ticker.upper()

    with open("company_tickers_exchange.json") as file:
        d = json.load(file)["data"]

    for stock in d:
        if stock[2] == ticker:
            return stock[0]

def top_n_tickers(n):
    res = []

    with open("company_tickers_exchange.json") as file:
        d = json.load(file)["data"]

    for i in range(n):
        stock = d[i]
        ticker = stock[2]

        res.append(ticker)

    return res
