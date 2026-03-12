import requests
import pandas as pd
from datetime import datetime, timedelta
import io
import os

def fetch_nse_data():
    # Advanced headers to mimic a high-end browser in India
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/csv,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en-IN;q=0.9,en;q=0.8',
        'Referer': 'https://www.nseindia.com/all-reports',
        'Connection': 'keep-alive'
    }
    
    session = requests.Session()
    # Step 1: Establish a "Session Handshake"
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
    except:
        return None

    # Step 2: Search backward to find the most recent successful trading day
    # (Since it's early Friday, it will likely find Thursday, March 12th)
    for i in range(1, 6): 
        check_date = datetime.now() - timedelta(days=i)
        date_str = check_date.strftime("%d%m%Y")
        url = f"https://www.nseindia.com/content/nsccl/fao_participant_oi_{date_str}.csv"
        
        try:
            response = session.get(url, headers=headers, timeout=10)
            if response.status_code == 200 and len(response.text) > 1000:
                df = pd.read_csv(io.StringIO(response.text), skiprows=1)
                df = df[df['Client Type'] != 'Total']
                df['Date'] = check_date.strftime("%Y-%m-%d")
                return df
        except:
            continue
    return None

if __name__ == "__main__":
    file_path = 'market_data.csv'
    new_data = fetch_nse_data()
    
    if new_data is not None:
        # Standardize columns
        new_data.columns = new_data.columns.str.strip()
        
        # Core Decoding Logic
        new_data['Net Index Fut'] = new_data['Future Index Long'] - new_data['Future Index Short']
        new_data['Net Index Call'] = new_data['Option Index Call Long'] - new_data['Option Index Call Short']
        new_data['Net Index Put'] = new_data['Option Index Put Long'] - new_data['Option Index Put Short']
        
        final_df = new_data[['Date', 'Client Type', 'Net Index Fut', 'Net Index Call', 'Net Index Put']]
        
        # Re-create file if missing, otherwise append
        if not os.path.exists(file_path):
            final_df.to_csv(file_path, index=False)
            print("✅ File was missing. Created new market_data.csv with data.")
        else:
            existing = pd.read_csv(file_path)
            if final_df['Date'].iloc[0] not in existing['Date'].astype(str).values:
                final_df.to_csv(file_path, mode='a', index=False, header=False)
                print(f"✅ Appended new data for {final_df['Date'].iloc[0]}")
    else:
        # Emergency fallback: ensure file exists so GitHub Action doesn't crash
        if not os.path.exists(file_path):
            pd.DataFrame(columns=['Date','Client Type','Net Index Fut','Net Index Call','Net Index Put']).to_csv(file_path, index=False)
            print("⚠️ Created header-only file because NSE connection failed.")
