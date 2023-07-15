import os
import yfinance as yf
import requests
from openpyxl import load_workbook

def update_stock_prices(filename, sheetname):
    # Load the workbook
    wb = load_workbook(filename)
    
    # Select the sheet
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


    # Save the workbook
    wb.save(filename)
    print("Stock prices updated successfully!")

filename = '../market.xlsx'  
lock_filename = "../.~lock.market.xlsx#"
lock_filename = "../.~lock.market.xlsx#"
sheetname = 'Stocks'


if not os.path.exists(lock_filename):
    update_stock_prices(filename, sheetname)
else:
    print("File already open")

