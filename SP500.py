
import requests
# import matplotlib.pyplot as plt
import pandas as pd  
import time
from datetime import datetime
from tinydb import TinyDB, Query
from threading import Thread
import talib


class SP500_ANALYZER:
    
    def __init__(self, stock):
        self.stock = stock
        print('analizer initialized...')
        self.yahooFinanceURL = "https://query1.finance.yahoo.com/v8/finance/chart/{0}?symbol={0}&period1={1}&period2={2}&interval={3}&includePrePost=true&events=div%7Csplit%7Cearn&lang=en-US&region=US&crumb=ED2zlWJHcMa&corsDomain=finance.yahoo.com"
        
    def get_Yahoo_Data(self):
        now = str(time.time()).split('.')[0]
        print('getting sp500 data', now)
        r = requests.get(self.yahooFinanceURL.format('%5EGSPC','1574186393', now, '30m'))
        sp500 = r.json()
        times = sp500["chart"]["result"][0]["timestamp"]
        quote = sp500["chart"]["result"][0]["indicators"]["quote"][0]
        data = {'Open': quote['open'] , 
                'Low': quote['low'] , 
                'High': quote['high'], 
                'Close': quote['close'],
                'Volume': quote['volume'],
                'Timestamp': times }
        df = pd.DataFrame(data) 
        self.moneyFlow = self.MFI(df, 14)
        
    def get_daily_Volume(self, stock):
        print('getting daily volume')
        now = str(time.time()).split('.')[0]
        s = str(datetime.today().date())
        startOfDay = str( time.mktime(datetime.strptime(s, "%Y-%m-%d").timetuple()) ).split('.')[0]
        r = requests.get(self.yahooFinanceURL.format(stock, startOfDay, now, '1d'))
        yahooData = r.json()
        return yahooData["chart"]["result"][0]["indicators"]["quote"][0]['volume']
        
    
        
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
    SP500_ANALYZER().__init__()