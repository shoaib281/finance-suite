import os
import yfinance as yf
import requests
from openpyxl import load_workbook
import pathlib

def update_stock_prices(filename, sheetname):
    wb = load_workbook(filename)
    
    sheet = wb[sheetname]

    for row in sheet.iter_rows(min_row=3):
        ticker_object = row[1]
        ticker = ticker_object.value

        if ticker != None:
            if ticker[0] != "-":

                stock = yf.Ticker(ticker)
                data = stock.history(period="1d")
                price = round(data["Close"][-1], 2)

                cell_name = "C" + str(ticker_object.row)

                sheet[cell_name].value = price


    wb.save(filename)
    print("Stock prices updated successfully!")

folderpath = pathlib.Path(__file__).parent.parent.resolve()
filename = folderpath / 'market.xlsx'  
lock_filename = folderpath / ".~lock.market.xlsx#"
sheetname = 'Stocks'


if not os.path.exists(lock_filename):
    update_stock_prices(filename, sheetname)
else:
    print("File already open")

