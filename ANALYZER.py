
import requests
# import matplotlib.pyplot as plt
import pandas as pd  
import time
from datetime import datetime
from tinydb import TinyDB, Query
from threading import Thread
import talib

yahooFinanceURL = "https://query1.finance.yahoo.com/v8/finance/chart/{0}?symbol={0}&period1={1}&period2={2}&interval={3}&includePrePost=true&events=div%7Csplit%7Cearn&lang=en-US&region=US&crumb=ED2zlWJHcMa&corsDomain=finance.yahoo.com"
db = TinyDB('DB.json')
running = True


class ANALYZER:
    
    def __init__(self):
        # self.stock = stock
        print('analizer initialized...')
        
        
    def get_Yahoo_Data(self, stock, beginning, timerange):
        now = str(time.time()).split('.')[0]
        print('getting Yahoo data', now)
        r = requests.get(yahooFinanceURL.format(stock, beginning, now, timerange))
        yahoo = r.json()
        times = yahoo["chart"]["result"][0]["timestamp"]
        quote = yahoo["chart"]["result"][0]["indicators"]["quote"][0]
        data = {'Open': quote['open'] , 
                'Low': quote['low'] , 
                'High': quote['high'], 
                'Close': quote['close'],
                'Volume': quote['volume'],
                'Timestamp': times }
        df = pd.DataFrame(data)
        return df
        
        
    def get_SP500_30minStateEvery15min(self):
        while running == True:
            monthAgo = time.time() - 2419200
            sp_df = self.get_Yahoo_Data('%5EGSPC', str(monthAgo).split('.')[0], '30m')
            moneyFlow = talib.MFI(sp_df, 14)
            Trade = Query()
            db.update({'SP500_30mMF': moneyFlow.values[-1:][0]}, Trade.type == 'current_state')
            time.sleep(900)
        
    # def slopeOFTheMF(df):
    #     for 

        
    def get_daily_Volume(self, stock):
        print('getting daily volume')
        now = str(time.time()).split('.')[0]
        s = str(datetime.today().date())
        startOfDay = str( time.mktime(datetime.strptime(s, "%Y-%m-%d").timetuple()) ).split('.')[0]
        r = requests.get(yahooFinanceURL.format(stock, startOfDay, now, '1d'))
        yahooData = r.json()
        return yahooData["chart"]["result"][0]["indicators"]["quote"][0]['volume']
    
    def look_for_SP500_volumeSpikes(self):
        print('checking daily volume spikes...')
        monthAgo = time.time() - 2419200
        sp_df = self.get_Yahoo_Data('%5EGSPC', str(monthAgo).split('.')[0], '1d')
        volumeSpkIndxs = sp_df.index[sp_df['Volume'] > sp_df['Volume'].mean() / 100 * 134]
        print('The number of volume spikes in the last month is %s', len(volumeSpkIndxs))
        for i in range(len(volumeSpkIndxs)):
            print(sp_df['Close'][volumeSpkIndxs[i]-1])
        if int(sp_df['Close'][volumeSpkIndxs[i]-1]) > int(sp_df['Close'][volumeSpkIndxs[i]]):
            print ('bearish volume', sp_df['Volume'][volumeSpkIndxs[i]])
        else:
            print ('bullish volume', sp_df['Volume'][volumeSpkIndxs[i]])
        
        
        
        
    
        
    # def get_price_action():
        
    # def get_20MA():
        
    # def get_overall_estimate():
        
    # def get_weekly_state():
        
    # def get_daily_state():
        
    # def get_4hour_state():
        
    # def get_1hour_state():
        
    # def get_30min_state():
        
    # def get_5min_state():
        
    # def get_2min_state():
    
if __name__=='__main__':
    Thread(target= ANALYZER().get_SP500_30minStateEvery15min).start()
    Thread(target=ANALYZER().get_daily_Volume, args=('TVIX',)).start()
