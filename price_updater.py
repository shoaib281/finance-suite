import os
import yfinance as yf
from openpyxl import load_workbook
import pathlib
import time
import logging

from loggingInit import log_function

logger = logging.getLogger(__name__)


@log_function
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

def percent_change_close_dataframe(df):
    first = df.iloc[0]["Close"]
    last = df.iloc[-1]["Close"]

    return (last / first) - 1


@log_function
def update_price_movements(sheetname):
    wb = load_workbook(filename)
    sheet = wb[sheetname]

    first_row = sheet[1]

    for row in sheet.iter_rows(min_row=3):
        ticker_object = row[1]
        ticker_row = ticker_object.row
        ticker = ticker_object.value

        if ticker != None:
            if ticker[0] != "-":
                stock = yf.Ticker(ticker)

                pct = []

                pct.append(percent_change_close_dataframe(stock.history(period="1d")))
                pct.append(percent_change_close_dataframe(stock.history(period="5d")))
                pct.append(percent_change_close_dataframe(stock.history(period="1mo")))
                pct.append(percent_change_close_dataframe(stock.history(period="3mo")))
                pct.append(percent_change_close_dataframe(stock.history(period="ytd")))
                pct.append(percent_change_close_dataframe(stock.history(period="1y")))

                for col_num, value in enumerate(pct):
                    sheet.cell(row=ticker_row, column=col_num + 3, value=value)

    sheet['A1'] = time.time()
    wb.save(filename)


folderpath = pathlib.Path(__file__).parent.parent.resolve()
filename = folderpath / 'market.xlsx'
lock_filename = folderpath / ".~lock.market.xlsx#"
sheets_fundemental = 'Fundemental'
sheets_movements = "Movements"


def main():
    if not os.path.exists(lock_filename):
        try:
            update_stock_prices(sheets_fundemental)
            update_price_movements(sheets_movements)
        except Exception as e:
            logger.exception(str(e))
    else:
        logger.info("File already open")


if __name__ == "__main__":
    main()
