import requests
import pandas as pd
from datetime import datetime, timedelta
import io
import os

def fetch_with_handshake():
    # Chrome-specific headers that NSE expects
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.nseindia.com/'
    }
    
    session = requests.Session()
    
    # STEP 1: Visit the main site to "wake up" the session and get cookies
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=15)
    except:
        return None

    # STEP 2: Try to find the most recent working day
    for i in range(1, 6): # Starts from yesterday since today's might not be out yet
        check_date = datetime.now() - timedelta(days=i)
        date_str = check_date.strftime("%d%m%Y")
        url = f"https://www.nseindia.com/content/nsccl/fao_participant_oi_{date_str}.csv"
        
        try:
            # We add a small delay so we don't look like a bot
            response = session.get(url, headers=headers, timeout=15)
            
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
    data = fetch_with_handshake()
    
    if data is not None:
        # Standardize column names (removes spaces)
        data.columns = data.columns.str.strip()
        
        # Calculate the 'Net' positions for your decoding logic
        data['Net Index Fut'] = data['Future Index Long'] - data['Future Index Short']
        data['Net Index Call'] = data['Option Index Call Long'] - data['Option Index Call Short']
        data['Net Index Put'] = data['Option Index Put Long'] - data['Option Index Put Short']
        
        # Keep only the columns your app needs
        final_df = data[['Date', 'Client Type', 'Net Index Fut', 'Net Index Call', 'Net Index Put']]
        
        # Overwrite the file with fresh data
        final_df.to_csv(file_path, index=False)
        print("✅ Data successfully decoded and saved.")
    else:
        print("❌ NSE is still blocking the request or file not found.")
