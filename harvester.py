import requests
import pandas as pd
from datetime import datetime, timedelta
import io
import os

def fetch_last_available_nse_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.nseindia.com/all-reports'
    }
    
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers, timeout=10)
    
    # Try looking back up to 5 days (to cover long weekends/holidays)
    for i in range(5):
        target_date = datetime.now() - timedelta(days=i)
        date_str = target_date.strftime("%d%m%Y")
        url = f"https://www.nseindia.com/content/nsccl/fao_participant_oi_{date_str}.csv"
        
        print(f"Checking NSE data for: {target_date.strftime('%Y-%m-%d')}...")
        
        try:
            response = session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                df = pd.read_csv(io.StringIO(response.text), skiprows=1)
                df = df[df['Client Type'] != 'Total']
                
                # Tag it with the actual date found in the file
                df['Date'] = target_date.strftime("%Y-%m-%d")
                print(f"✅ Success! Found data for {target_date.strftime('%Y-%m-%d')}")
                return df
        except Exception as e:
            continue
            
    return None

if __name__ == "__main__":
    file_path = 'market_data.csv'
    new_data = fetch_last_available_nse_data()
    
    if new_data is not None:
        # 1. Calculate Net Columns
        new_data['Net Index Fut'] = new_data['Future Index Long'] - new_data['Future Index Short']
        new_data['Net Index Call'] = new_data['Option Index Call Long'] - new_data['Option Index Call Short']
        new_data['Net Index Put'] = new_data['Option Index Put Long'] - new_data['Option Index Put Short']
        
        # 2. Check for Duplicates (Don't append if the date already exists in our CSV)
        if os.path.exists(file_path):
            existing_df = pd.read_csv(file_path)
            last_date_in_csv = existing_df['Date'].max()
            new_date_found = new_data['Date'].iloc[0]
            
            if last_date_in_csv == new_date_found:
                print("⚠️ Data for this date already exists in the CSV. Skipping append.")
            else:
                new_data.to_csv(file_path, mode='a', index=False, header=False)
                print(f"🚀 Appended new data for {new_date_found}")
        else:
            new_data.to_csv(file_path, index=False)
            print("🆕 Created new market_data.csv with first entry.")
    else:
        print("❌ Could not find any NSE data in the last 5 days.")
