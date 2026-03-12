import requests
import pandas as pd
from datetime import datetime, timedelta
import io
import os

def fetch_nse_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.nseindia.com/all-reports'
    }
    session = requests.Session()
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
    except:
        return None

    # Look back 5 days to find the last active market day
    for i in range(5):
        check_date = datetime.now() - timedelta(days=i)
        date_str = check_date.strftime("%d%m%Y")
        url = f"https://www.nseindia.com/content/nsccl/fao_participant_oi_{date_str}.csv"
        
        try:
            response = session.get(url, headers=headers, timeout=10)
            if response.status_code == 200 and len(response.text) > 500:
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
        # Calculate Net Positions for your analysis
        new_data['Net Index Fut'] = new_data['Future Index Long'] - new_data['Future Index Short']
        new_data['Net Index Call'] = new_data['Option Index Call Long'] - new_data['Option Index Call Short']
        new_data['Net Index Put'] = new_data['Option Index Put Long'] - new_data['Option Index Put Short']
        
        if not os.path.exists(file_path):
            # Create NEW file if you accidentally deleted it
            new_data.to_csv(file_path, index=False)
            print("✅ Created new market_data.csv")
        else:
            existing = pd.read_csv(file_path)
            if new_data['Date'].iloc[0] not in existing['Date'].astype(str).values:
                new_data.to_csv(file_path, mode='a', index=False, header=False)
                print(f"✅ Appended data for {new_data['Date'].iloc[0]}")
            else:
                print("ℹ️ Data already exists for this date.")
    else:
        # CRITICAL: If no data found, create a blank file with headers 
        # so the 'git add' command doesn't crash the Action.
        if not os.path.exists(file_path):
            pd.DataFrame(columns=['Date','Client Type','Net Index Fut','Net Index Call','Net Index Put']).to_csv(file_path, index=False)
            print("⚠️ No NSE data found, created empty file with headers.")
