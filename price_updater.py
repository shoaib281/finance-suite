import os
import yfinance as yf
import requests
from openpyxl import load_workbook
import pathlib
import time
import logging

def update_stock_prices(sheetname):
    wb = load_workbook(filename)
    sheet = wb[sheetname]
    sheet['A1'] = time.time()

    for row in sheet.iter_rows(min_row=3):
        ticker_object = row[1]
        ticker = ticker_object.value

        if ticker != None:
            if ticker[0] != "-":

                stock = yf.Ticker(ticker)
                data = stock.history(period="5d")
                price = round(data["Close"][-1], 2)

                cell_name = "C" + str(ticker_object.row)

                sheet[cell_name].value = price


    wb.save(filename)
    logging.info("Stock prices updated successfully!")

def percent_change_close_dataframe(df):
    first = df.iloc[0]["Close"]
    last = df.iloc[-1]["Close"]

    return (last / first) - 1


def update_price_movements(sheetname):
    wb = load_workbook(filename)
    sheet = wb[sheetname]
    sheet['A1'] = time.time()

    first_row = sheet[1]

    for row in sheet.iter_rows(min_row=3):
        ticker_object = row[1]
        ticker_row = ticker_object.row
        ticker = ticker_object.value

        if ticker != None:
            if ticker[0] != "-":
                stock = yf.Ticker(ticker)
                
                pct = []

                pct.append(percent_change_close_dataframe(stock.history(period="2d")))
                pct.append(percent_change_close_dataframe(stock.history(period="5d")))
                pct.append(percent_change_close_dataframe(stock.history(period="1mo")))
                pct.append(percent_change_close_dataframe(stock.history(period="3mo")))
                pct.append(percent_change_close_dataframe(stock.history(period="ytd")))
                pct.append(percent_change_close_dataframe(stock.history(period="1y")))

                for col_num, value in enumerate(pct):
                    sheet.cell(row = ticker_row, column=col_num + 3, value=value)


    wb.save(filename)
    logging.info("Stock prices updated successfully!")


curPath = pathlib.Path(__file__).parent.resolve()
folderpath = pathlib.Path(__file__).parent.parent.resolve()
filename = folderpath / 'market.xlsx'  
lock_filename = folderpath / ".~lock.market.xlsx#"
sheets_fundemental = 'Fundemental'
sheets_movements = "Movements"

logging.basicConfig(
        filename = curPath / "log", 
        level=logging.INFO,
        #format='%(asctime)s %(levelname)-8s %(message)s',
        format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
)

# Configure logger to write to a file...

def my_handler(type, value, tb):
    logging.exception("Uncaught exception: {0}".format(str(value)))

import sys
sys.excepthook = my_handler


if not os.path.exists(lock_filename):
    try:
        update_stock_prices(sheets_fundemental)
        update_price_movements(sheets_movements)
    except Exception as e:
        logging.exception(str(e))
else:
    logging.info("File already open")

