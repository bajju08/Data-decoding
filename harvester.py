import requests
import pandas as pd
from datetime import datetime
import io
import os

def get_nse_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    date_str = datetime.now().strftime("%d%m%Y")
    url = f"https://www.nseindia.com/content/nsccl/fao_participant_oi_{date_str}.csv"
    
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        df = pd.read_csv(io.StringIO(response.text), skiprows=1)
        # Drop the 'Total' row
        df = df[df['Client Type'] != 'Total']
        
        # --- Decoding Logic ---
        df['Date'] = datetime.now().strftime("%Y-%m-%d")
        df['Net Index Fut'] = df['Future Index Long'] - df['Future Index Short']
        df['Net Index Call'] = df['Option Index Call Long'] - df['Option Index Call Short']
        df['Net Index Put'] = df['Option Index Put Long'] - df['Option Index Put Short']
        
        # Calculation for PCR per participant
        df['PCR'] = df['Option Index Put Long'] / df['Option Index Call Long']
        
        return df
    return None

if __name__ == "__main__":
    data = get_nse_data()
    if data is not None:
        file_path = 'market_data.csv'
        data.to_csv(file_path, mode='a', index=False, header=not os.path.exists(file_path))
        print("Success: Data harvested and decoded.")
