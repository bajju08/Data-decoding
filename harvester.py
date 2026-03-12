import requests
import pandas as pd
from datetime import datetime, timedelta
import io
import os

def fetch_most_recent_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.nseindia.com/all-reports'
    }
    
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers, timeout=10)
    
    # Check today, then yesterday, then the day before...
    for i in range(5):
        check_date = datetime.now() - timedelta(days=i)
        date_str = check_date.strftime("%d%m%Y")
        url = f"https://www.nseindia.com/content/nsccl/fao_participant_oi_{date_str}.csv"
        
        print(f"Checking for data on {check_date.strftime('%Y-%m-%d')}...")
        
        try:
            response = session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                df = pd.read_csv(io.StringIO(response.text), skiprows=1)
                df = df[df['Client Type'] != 'Total']
                df['Date'] = check_date.strftime("%Y-%m-%d")
                return df
        except:
            continue
    return None

if __name__ == "__main__":
    file_path = 'market_data.csv'
    new_data = fetch_most_recent_data()
    
    if new_data is not None:
        # Calculate Net Positions
        new_data['Net Index Fut'] = new_data['Future Index Long'] - new_data['Future Index Short']
        new_data['Net Index Call'] = new_data['Option Index Call Long'] - new_data['Option Index Call Short']
        new_data['Net Index Put'] = new_data['Option Index Put Long'] - new_data['Option Index Put Short']
        
        # Save logic: If file exists, check if this date is already there
        if os.path.exists(file_path):
            existing = pd.read_csv(file_path)
            # Avoid duplicate entries for the same date
            if new_data['Date'].iloc[0] not in existing['Date'].values:
                new_data.to_csv(file_path, mode='a', index=False, header=False)
                print(f"Success: Added data for {new_data['Date'].iloc[0]}")
            else:
                print(f"Data for {new_data['Date'].iloc[0]} already exists. Skipping.")
        else:
            new_data.to_csv(file_path, index=False)
            print("Success: Created new file with latest data.")
    else:
        print("Error: No data found in the last 5 days.")
