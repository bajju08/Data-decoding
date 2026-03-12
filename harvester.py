import requests
import pandas as pd
from datetime import datetime
import os

def harvest_nse_data():
    date_str = datetime.now().strftime("%d%m%Y")
    url = f"https://www.nseindia.com/content/nsccl/fao_participant_oi_{date_str}.csv"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        # Process and append to market_data.csv
        new_data = pd.read_csv(pd.compat.StringIO(response.text), skiprows=1)
        # Add timestamp and logic...
        new_data.to_csv('market_data.csv', mode='a', header=not os.path.exists('market_data.csv'))
        print("Data Harvested Successfully.")

if __name__ == "__main__":
    harvest_nse_data()