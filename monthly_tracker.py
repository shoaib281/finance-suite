import warnings
import webbrowser
warnings.filterwarnings('ignore')

import pandas as pd
import argparse
from odf.opendocument import OpenDocumentSpreadsheet
from odf.table import Table, TableRow, TableCell
from odf.text import P
import os
import subprocess
from odf.opendocument import OpenDocumentSpreadsheet
from odf.style import Style, TableColumnProperties
from odf.table import Table, TableColumn, TableRow, TableCell
from odf.text import P
import glob

import numpy as np

def add_day_of_week(df):
    print("Starting add_day_of_week...")
    df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y")
    df.insert(1, 'DayOfWeek', df['Date'].dt.day_name())
    print("Finished add_day_of_week.")
    return df

def sort_by_date(df):
    print("Starting sort_by_date...")
    df['Date'] = pd.to_datetime(df['Date'])
    df['Date'] = df['Date'].dt.date
    print("Finished sort_by_date.")
    return df.sort_values(by='Date', ascending=True).reset_index(drop=True)

def separate_gwr(df):
    print("Starting separate_gwr...")
    gwr_df = df[df['Description'].str.contains("GWR", case=False, na=False)]
    non_gwr_df = df[~df['Description'].str.contains("GWR", case=False, na=False)]

    empty_data = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            empty_data[col] = np.nan
        else:
            empty_data[col] = ""
    empty_row = pd.DataFrame([empty_data])

    result = pd.concat([non_gwr_df, empty_row, gwr_df], ignore_index=True)
    print("Finished separate_gwr.")
    return result

def remove_balance_column(df):
    print("Starting remove_balance_column...")
    df = df.drop(columns=['Balance'])
    print("Finished remove_balance_column.")
    return df

def create_table_with_special_widths(df, doc):
    table = Table(name="Sheet1")
    wide_column_style = Style(name="WideCol", family="table-column")
    wide_column_style.addElement(TableColumnProperties(columnwidth="10cm"))
    doc.automaticstyles.addElement(wide_column_style)
    columns_to_adjust = [2]
    for i in range(len(df.columns)):
        if i in columns_to_adjust:
            table.addElement(TableColumn(stylename=wide_column_style))
        else:
            table.addElement(TableColumn())
    return table

def save_as_ods(df, output_file):
    print("Starting save_as_ods...")
    doc = OpenDocumentSpreadsheet()
    table = create_table_with_special_widths(df, doc)
    header_row = TableRow()
    for col in df.columns:
        cell = TableCell()
        cell.addElement(P(text=str(col)))
        header_row.addElement(cell)
    table.addElement(header_row)

    for _, row in df.iterrows():
        tr = TableRow()
        for col_name, item in zip(df.columns, row):
            if pd.api.types.is_numeric_dtype(df[col_name]):
                cell = TableCell(valuetype="float", value=item)
                cell.addElement(P(text=str(item)))
            else:
                cell = TableCell()
                cell.addElement(P(text=str(item)))
            tr.addElement(cell)
        table.addElement(tr)


    doc.spreadsheet.addElement(table)
    doc.save(output_file)
    print(f"✅ Processed ODS saved to {output_file}")

def fix_df_types(df):
    print("Fixing types")
    df['Amount'] = df['Amount'].replace({',': '', '£': '', '$': ''}, regex=True)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    print("Finished fixing types")
    return df


def process_csv(input_file, output_file):
    print("Starting process_csv...")
    df = pd.read_csv(input_file)
    df = remove_balance_column(df)
    df = fix_df_types(df)
    df = add_day_of_week(df)
    df = sort_by_date(df)
    df = separate_gwr(df)
    save_as_ods(df, output_file)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    portfolio_path = os.path.abspath(os.path.join(script_dir, '../portfolio.ods'))

    try:
        if os.name == "nt":
            os.startfile(output_file)
            os.startfile(portfolio_path)

        elif os.name == "posix":
            subprocess.call(["xdg-open", output_file])
            subprocess.call(["xdg-open", portfolio_path])


        delete_original_csv(input_file)
    except Exception as e:
        print(f"⚠️ Could not open file automatically: {e}")

    print("Finished process_csv.")

def find_first_csv_in_monthly():
    print("Searching for CSV file...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_directory = os.path.abspath(os.path.join(current_dir, '../monthly'))

    csv_files = glob.glob(os.path.join(input_directory, '*.csv'))
    if csv_files:
        print(f"Found CSV file: {csv_files[0]}")
        return csv_files[0]
    else:
        print(f"No CSV files found in the directory: {input_directory}")
        return None

def delete_original_csv(file_path):
    print("Starting delete_original_csv...")
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"✅ Original CSV file deleted: {file_path}")
    else:
        print(f"⚠️ Original CSV file not found, skipping deletion: {file_path}")
    print("Finished delete_original_csv.")

def open_sites():
    webbrowser.open_new_tab("https://www.amazon.co.uk/gp/css/order-history?ref_=nav_orders_first")


if __name__ == "__main__":
    input_file_path = find_first_csv_in_monthly()
    if input_file_path:
        open_sites()
        output_directory = os.path.dirname(input_file_path)
        output_file_path = os.path.join(output_directory, "transformed.ods")
        process_csv(input_file_path, output_file_path)
    else:
        print("Processing aborted due to missing input file.")

