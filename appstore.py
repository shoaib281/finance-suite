import requests
import sqlite3
from datetime import datetime
import logging

from utils import copy_to_clipboard
from utils import FOLDERPATH

COUNT = 100
URL = f"https://rss.applemarketingtools.com/api/v2/us/apps/top-free/{COUNT}/apps.json"
RETRIES = 3

DB_PATH = FOLDERPATH / "data" / "data.db"


def write_tickers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    initialize_database(cursor)

    cursor.execute(f"SELECT * FROM artist_security_mapping WHERE ticker IS NULL")
    rows_with_null = cursor.fetchall()

    for row in rows_with_null:
        companyName = row[0]

        copy_to_clipboard(companyName + " stock ticker")
        ticker = input(f"Enter a value for {companyName}: ").upper()

        cursor.execute(
            f"""
            UPDATE artist_security_mapping
            SET ticker = ?
            WHERE artistName = ?
        """,
            (ticker, companyName),
        )  # Assuming 'id' is the primary key

    conn.commit()
    cursor.close()


def initialize_database(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS artist_security_mapping (
            artistName TEXT NOT NULL PRIMARY KEY,
            ticker TEXT
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS artist_app_mapping (
            appID INTEGER PRIMARY KEY,
            appName TEXT NOT NULL,
            artistName TEXT NOT NULL,
            FOREIGN KEY (artistName) REFERENCES artist_security_mapping(artistName)
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS us_app_store_rankings (
            id INTEGER PRIMARY KEY,
            appID INTEGER NOT NULL, 
            rank INTEGER NOT NULL,
            date TEXT NOT NULL,
            
            FOREIGN KEY (appID) REFERENCES artist_app_mapping(appID)
            UNIQUE(rank, date)
        )
    """
    )


def main():
    logging.info("Starting")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    initialize_database(cursor)
    conn.commit()

    today = datetime.today().strftime("%Y-%m-%d")

    for _ in range(RETRIES):
        response = requests.get(URL)

        if response.status_code == 200:
            data = response.json()
            results = data["feed"]["results"]

            for rank in range(COUNT):
                result = results[rank]

                artistName = result["artistName"]
                appID = int(result["id"])
                appName = result["name"]

                cursor.execute(
                    f"""
                    INSERT OR IGNORE INTO artist_security_mapping (artistName)
                    VALUES (?)
                """,
                    (artistName,),
                )

                cursor.execute(
                    f"""
                    INSERT OR REPLACE INTO artist_app_mapping (appID, appName, artistName)
                    VALUES (?, ?, ?)
                """,
                    (
                        appID,
                        appName,
                        artistName,
                    ),
                )

                cursor.execute(
                    f"""
                    INSERT OR REPLACE INTO us_app_store_rankings (appID, rank, date)
                    VALUES (?, ?, ?)
                """,
                    (
                        appID,
                        rank,
                        today,
                    ),
                )
            break

    conn.commit()
    cursor.close()

    logging.info("ending")


if __name__ == "__main__":
    main()
