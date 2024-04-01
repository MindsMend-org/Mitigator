# PRIVATE AND CONFIDENTIAL [Intellectual Property Of Brett Palmer mince@foldingcircles.co.uk]
# [No Copying Or Reading Or Use Permitted !]
"""
Copyright (c) 2023, Brett Palmer (Mince@foldingcircles.co.uk)

All rights reserved. No permission is granted for anyone, except the software owner, Brett Palmer, to use, copy, modify,
distribute, sublicense, or otherwise deal with the software in any manner.

Any unauthorized use, copying, or distribution of this software without the explicit written consent of the software
owner is strictly prohibited.

For permission requests, please contact the software owner, Brett Palmer, at Mince@foldingcircles.co.uk.
"""

# FoldingCircles Making The Unknown Known


__version__ = "0.0.001"
print(f'forex_data_loader.py {__version__}')
UPDATE_FOREX = False


# forex_data_loader.py
import csv
from datetime import datetime  # Correct import for datetime

class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        data = []
        with open(self.file_path, 'r') as file:
            csv_reader = csv.DictReader(file)  # Use DictReader to read data into a dictionary
            for row in csv_reader:
                date = datetime.strptime(row['Date'], "%Y-%m-%d")
                open_price = float(row['Open'])
                close_price = float(row['Close'])
                high_price = float(row['High'])
                low_price = float(row['Low'])
                data.append({
                    'timestamp': date,
                    'open': open_price,
                    'close': close_price,
                    'high': high_price,
                    'low': low_price
                })
        return data

# Alpha Vantage website (https://www.alphavantage.co/)
#  0B1ZE4ZQ7EGFTBHO
# pip install requests
import requests
import pandas as pd

def fetch_forex_data(symbol, api_key):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "FX_DAILY",
        "from_symbol": symbol[:3],
        "to_symbol": symbol[3:],
        "apikey": api_key,
        "outputsize": "full",
        "datatype": "json"
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    # Convert the data to a pandas DataFrame (optional)
    df = pd.DataFrame(data['Time Series FX (Daily)']).T
    df.columns = ['Open', 'Close', 'High', 'Low']
    return df

def save_data(df, filename):
    df.to_csv(filename, index_label='Date')
    print(f"Data saved to CSV file. [{filename}]")

def pull_forex_data():
    # Example usage
    api_key = '0B1ZE4ZQ7EGFTBHO'  # Replace with your Alpha Vantage API key
    currency_pairs = ['EURUSD', 'USDJPY', 'GBPUSD', 'AUDUSD', 'USDCAD', 'USDCHF', 'NZDUSD']

    # usdjpy_data = fetch_forex_data("USDJPY", api_key)
    # audjpy_data = fetch_forex_data("AUDJPY", api_key)

    # Save the data to CSV files
    for pair in currency_pairs:
        forex_data = fetch_forex_data(pair, api_key)
        save_data(forex_data, f'{pair}_data.csv')
        print(forex_data.head())  # Print the first few rows of each pair


# UPDATE_FOREX = False

if UPDATE_FOREX: pull_forex_data()