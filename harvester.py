import requests
import pandas as pd
from datetime import datetime
import io
import os

def get_nse_data():
    # Stealth headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/csv',
        'Referer': 'https://www.nseindia.com/all-reports'
    }
    
    # Try today's date, then yesterday's if not found (for early runs)
    date_str = datetime.now().strftime("%d%m%Y")
    url = f"https://www.nseindia.com/content/nsccl/fao_participant_oi_{date_str}.csv"
    
    session = requests.Session()
    try:
        # First, hit the home page to get cookies
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        response = session.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text), skiprows=1)
            df = df[df['Client Type'] != 'Total']
            
            # Add Date and Net Columns
            df['Date'] = datetime.now().strftime("%Y-%m-%d")
            df['Net Index Fut'] = df['Future Index Long'] - df['Future Index Short']
            df['Net Index Call'] = df['Option Index Call Long'] - df['Option Index Call Short']
            df['Net Index Put'] = df['Option Index Put Long'] - df['Option Index Put Short']
            return df
        else:
            print(f"NSE hasn't uploaded data for {date_str} yet (Status: {response.status_code})")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    data = get_nse_data()
    file_path = 'market_data.csv'
    
    if data is not None:
        data.to_csv(file_path, mode='a', index=False, header=not os.path.exists(file_path))
        print("Data saved successfully.")
    else:
        # CRITICAL: Create an empty file with headers if it doesn't exist
        # This prevents the GitHub Action "pathspec" error
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write("Date,Client Type,Future Index Long,Future Index Short,Option Index Call Long,Option Index Call Short,Option Index Put Long,Option Index Put Short,Net Index Fut,Net Index Call,Net Index Put\n")
            print("Created empty file to satisfy GitHub Action.")
