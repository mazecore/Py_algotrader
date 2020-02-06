
import requests
# import matplotlib.pyplot as plt
import pandas as pd  
import time
from datetime import datetime
from tinydb import TinyDB, Query
from threading import Thread
import talib
import math

yahooFinanceURL = "https://query1.finance.yahoo.com/v8/finance/chart/{0}?symbol={0}&period1={1}&period2={2}&interval={3}&includePrePost=true&events=div%7Csplit%7Cearn&lang=en-US&region=US&crumb=ED2zlWJHcMa&corsDomain=finance.yahoo.com"
db = TinyDB('DB.json')
running = True


class ANALYZER:
    
    def __init__(self):
        # self.stock = stock
        print('analizer initialized...')
        Thread(target = self.look_for_SP500_volumeSpikes).start()
        Thread(target = self.get_SP500_5minStateEvery1min).start()
        Thread(target = self.get_SP500_30minStateEvery15min).start()
        Thread(target = self.get_daily_Volume, args=('TVIX',)).start()
        
        
    def get_Yahoo_Data(self, stock, beginning, interval):
        now = str(time.time()).split('.')[0]
        print('getting Yahoo data', now)
        r = requests.get(yahooFinanceURL.format(stock, beginning, now, interval))
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
    
    def get_SP500_5minStateEvery1min(self):
        while running == True:
            weekAgo = time.time() - 386329
            sp_df = self.get_Yahoo_Data('%5EGSPC', str(weekAgo).split('.')[0], '5m')
            moneyFlow = talib.MFI(sp_df, 14)
            rateOfChange = talib.ROC(sp_df, 14)
            
            print('last 10 values of latest 5 min Money Flow:')
            print(moneyFlow[-10:])
            
            print('last 10 values of latest 5 min Rate Of Change:')
            print(rateOfChange[-10:])
            
            fiveMinMF_lastValue = moneyFlow.values[-1:][0]
            fiveMinROC_lastValue = rateOfChange.values[-1:][0]
            
            if math.isnan(fiveMinMF_lastValue):
                fiveMinMF_lastValue = moneyFlow.values[-2:][0]
                if math.isnan(moneyFlow.values[-2:][0]):
                   fiveMinMF_lastValue = moneyFlow.values[-3:][0]
            print('5min Money Flow is = ', fiveMinMF_lastValue)
            Trade = Query()
            db.update({'SP500_5mMF': fiveMinMF_lastValue }, Trade.type == 'current_state')
            db.update({'SP500_5mROC': fiveMinROC_lastValue }, Trade.type == 'current_state')
            if fiveMinMF_lastValue != 'NaN' and fiveMinROC_lastValue != 'NaN':
                fiveMinUltimateIndicator = fiveMinMF_lastValue 
            time.sleep(60)


    def get_SP500_30minStateEvery15min(self):
        while running == True:
            monthAgo = time.time() - 2419200
            sp_df = self.get_Yahoo_Data('%5EGSPC', str(monthAgo).split('.')[0], '30m')
            moneyFlow = talib.MFI(sp_df, 14)
            thirtyMinMF_lastValue = moneyFlow.values[-1:][0]
            
            print('last 10 values of latest 30 min Money Flow:')
            print(moneyFlow[-10:])
            
            if math.isnan(thirtyMinMF_lastValue):
                thirtyMinMF_lastValue = moneyFlow.values[-2:][0]
                if math.isnan(moneyFlow.values[-2:][0]):
                   thirtyMinMF_lastValue = moneyFlow.values[-3:][0]
            Trade = Query()
            db.update({'SP500_30mMF': thirtyMinMF_lastValue }, Trade.type == 'current_state')
            time.sleep(900)

#           this still tracks only 1 hr Money Flow
    def get_SP500_4hrStateEvery1hour(self):
        while running == True:
            monthAgo = time.time() - 2419200
            sp_df = self.get_Yahoo_Data('%5EGSPC', str(monthAgo).split('.')[0], '60m')
            moneyFlow = talib.MFI(sp_df, 14)
            print('last 10 values of latest 1hr Money Flow:')
            Trade = Query()
            db.update({'SP500_4hrMF': moneyFlow.values[-1:][0]}, Trade.type == 'current_state')
            time.sleep(3600)
        
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
        volSpkIndxes = sp_df.index[sp_df['Volume'] > sp_df['Volume'].mean() / 100 * 134]
        print('The number of volume spikes in the last month is %s', len(volSpkIndxes))
        Trade = Query()
        for i in range(len(volSpkIndxes)):
            spike = { 'volume': sp_df['Volume'][volSpkIndxes[i]], 'date': sp_df['Timestamp'][volSpkIndxes[i]], 'sentiment': None }
            if int(sp_df['Close'][volSpkIndxes[i]-1]) > int(sp_df['Close'][volSpkIndxes[i]]):
                spike['sentiment'] = 'Bearish'
                print ('bearish volume', sp_df['Volume'][volSpkIndxes[i]])
            else:
                spike['sentiment'] = 'Bullish'
                print ('bullish volume', sp_df['Volume'][volSpkIndxes[i]])
            db.update({'SP500_lastVolumeSpike': spike }, Trade.type == 'current_state')
        # don't forget to mark attitude towards long term prospect depending on these spikes
        
        
        
        
    
        
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
    
#if __name__=='__main__':
#    print('if name main analyzer runs')
#    Thread(target=ANALYZER().look_for_SP500_volumeSpikes).start()
#    Thread(target= ANALYZER().get_SP500_5minStateEvery1min).start()
#    Thread(target= ANALYZER().get_SP500_30minStateEvery15min).start()
#    Thread(target=ANALYZER().get_daily_Volume, args=('TVIX',)).start()
