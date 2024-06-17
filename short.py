import pandas as pd
import json
import requests


class ShortManager:
    def __init__(self):
        with open("credentials.json") as file:
            data = json.load(file)

        api_key = data["finra_api"]

        headers = {
            "Authorization": f"Basic {api_key}",
        }

        params = {
            "grant_type": "client_credentials",
        }

        response = requests.post(
            "https://ews.fip.finra.org/fip/rest/ews/oauth2/access_token",
            params=params,
            headers=headers,
        )
        data = response.json()

        access = data["access_token"]
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {access}",
        }
        self.fields = [
            "currentShortPositionQuantity",
            "settlementDate",
            "daysToCoverQuantity",
        ]
        self.short_api = (
            "https://api.finra.org/data/group/otcmarket/name/consolidatedShortInterest"
        )

    def get_data(self, ticker):
        customFilter = {
            "fields": self.fields,
            "compareFilters": [
                {
                    "compareType": "equal",
                    "fieldName": "symbolCode",
                    "fieldValue": ticker,
                }
            ],
        }

        response = requests.post(
            self.short_api, headers=self.headers, json=customFilter
        )
        results = pd.json_normalize(response.json())
        results = results.sort_values("settlementDate")

        return results


# a = ShortManager()
# a.get_data("AAPL")
