import requests
import pandas as pd
from datetime import datetime, timedelta
import io
import os

def fetch_nse_with_cookies():
    # 1. Setup headers to look like a real Chrome browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    
    session = requests.Session()
    
    # 2. THE SECRET STEP: Visit the home page first to get the session cookies
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
    except Exception as e:
        print(f"Failed to connect to NSE Home: {e}")
        return None

    # 3. Look back up to 5 days to find the last working day
    for i in range(5):
        check_date = datetime.now() - timedelta(days=i)
        date_str = check_date.strftime("%d%m%Y")
        url = f"https://www.nseindia.com/content/nsccl/fao_participant_oi_{date_str}.csv"
        
        print(f"Attempting to fetch data for: {check_date.strftime('%Y-%m-%d')}...")
        
        try:
            response = session.get(url, headers=headers, timeout=10)
            
            # If 200, we found it!
            if response.status_code == 200 and len(response.text) > 500:
                df = pd.read_csv(io.StringIO(response.text), skiprows=1)
                df = df[df['Client Type'] != 'Total']
                df['Date'] = check_date.strftime("%Y-%m-%d")
                return df
            else:
                print(f"Data not available for {date_str} (Status: {response.status_code})")
        except Exception as e:
            print(f"Error on {date_str}: {e}")
            continue
            
    return None

if __name__ == "__main__":
    file_path = 'market_data.csv'
    new_data = fetch_nse_with_cookies()
    
    if new_data is not None:
        # Calculate Decoded Columns
        new_data['Net Index Fut'] = new_data['Future Index Long'] - new_data['Future Index Short']
        new_data['Net Index Call'] = new_data['Option Index Call Long'] - new_data['Option Index Call Short']
        new_data['Net Index Put'] = new_data['Option Index Put Long'] - new_data['Option Index Put Short']
        
        # Save or Append
        if os.path.exists(file_path):
            existing = pd.read_csv(file_path)
            # Prevent double-entry for the same date
            if new_data['Date'].iloc[0] not in existing['Date'].astype(str).values:
                new_data.to_csv(file_path, mode='a', index=False, header=False)
                print(f"✅ Appended data for {new_data['Date'].iloc[0]}")
            else:
                print(f"ℹ️ Data for {new_data['Date'].iloc[0]} already exists.")
        else:
            new_data.to_csv(file_path, index=False)
            print(f"✅ Created new file with data for {new_data['Date'].iloc[0]}")
    else:
        print("❌ Failed to find any data in the last 5 days. Check NSE website status.")
