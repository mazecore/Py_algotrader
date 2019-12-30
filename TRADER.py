# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 19:57:19 2019

@author: Ldeezy
"""
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
# from bs4 import BeautifulSoup

import requests
# import matplotlib.pyplot as plt
import pandas as pd  
import time
from datetime import datetime
from tinydb import TinyDB, Query



class TRADER:
    
    def __init__(self):
        print(str(datetime.now()).split('.')[0])
        self.browser = webdriver.Chrome('C:\chromedriver')
        # self.bidsAreHigh = false
        self.yahooFinanceURL = "https://query1.finance.yahoo.com/v8/finance/chart/{0}?symbol={0}&period1={1}&period2={2}&interval={3}&includePrePost=true&events=div%7Csplit%7Cearn&lang=en-US&region=US&crumb=ED2zlWJHcMa&corsDomain=finance.yahoo.com"
        self.browser.get('http://markets.cboe.com/us/equities/market_statistics/book_viewer/')
        self.limit_order_pending = False
        self.stock_purchased = False
        self.db = TinyDB('DB.json')
        record = Query()
        self.maCash = (self.db.search(record.type == 'current_state'))[0]['cash_amount']
        print(self.maCash)
        self.tradeNumber = 0
        self.change_Stock_and_go_to_EDGX('TVIX')

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
        
    def change_Stock_and_go_to_EDGX(self, stock):
        inputt = self.browser.find_element_by_xpath('//*[@id="symbol0"]')
        print('switching stock to tvix')
        actions = ActionChains(self.browser)
        actions.move_to_element(inputt)
        actions.double_click(inputt)
        actions.send_keys(Keys.BACKSPACE)
        actions.send_keys(stock)
        actions.send_keys(Keys.ENTER)
        actions.pause(1)
        EDGX = self.browser.find_element_by_xpath('//span[text()="EDGX Equities"]')
        print('going to EDGX')
        actions.click(EDGX)
        actions.pause(1)
        actions.perform()
        time.sleep(1)
        self.get_info_table()

    def MFI(df, n):

        PP = (df['High'] + df['Low'] + df['Close']) / 3
        i = 0
        PosMF = [0]
        while i < len(df) - 1:  # df.index[-1]:
            if PP[i + 1] > PP[i]:
                PosMF.append(PP[i + 1] * df.iat[i + 1, df.columns.get_loc('Volume')])
            else:
                PosMF.append(0)
            i=i + 1
        PosMF = pd.Series(PosMF)
        TotMF = PP * df['Volume']
        MFR = pd.Series(PosMF / TotMF)
        result = pd.Series(MFR.rolling(n).mean(), name='MFI_' + str(n))
        return result


    def set_limit_order(self, price, n):
        if self.currentPrice > price:
            self.limit_order_pending = True
        else:
            self.buy(price, n)
            self.stock_purchased = True
            
            
    def buy(self, stockPrice, n):
        if self.currentPrice <= stockPrice:
            self.maCash = self.maCash - stockPrice * n
            print('bought at %s', stockPrice)
            self.register_the_trade(n, stockPrice, 'purchase')
        
    def sell(self, stockPrice, n):
        if self.currentPrice >= stockPrice:
            self.maCash = self.maCash + stockPrice * n
            print('sold at %s', stockPrice)
            self.register_the_trade(n, stockPrice, 'sale')


    def check_stock_info(self):
        self.currentPrice = float(self.last10TradesPrices[0].text)
        if self.stock_purchased == False:
            i = 0
            for j in self.topBidShares:
                if int(j.text) > 1600:
                    self.buy(float(self.topBidsPrice[i].text), 500)
                i = i + 1
        else:
            b = 0
            for s in self.topAskShares:
                if int(s.text) >= 1600:
                    self.sell(float(self.topAskPrice[b].text), 500)
                b = b + 1
                        

    def get_info_table(self):
        self.last10TradesPrices = self.browser.find_elements_by_class_name("book-viewer__trades-price")
        self.topBidsPrice = self.browser.find_elements_by_class_name("book-viewer__bid-price")
        self.topBidShares = self.browser.find_elements_by_class_name("book-viewer__bid-shares")
        self.topAskPrice = self.browser.find_elements_by_class_name("book-viewer__ask-price")
        self.topAskShares = self.browser.find_elements_by_class_name("book-viewer__ask-shares")
        self.set_interval()


    def set_interval(self):
        while True:
            time.sleep(5)
            self.check_stock_info()
            
    def register_the_trade(self, n, stockPrice, transactionType):
        Trade = Query()
        self.db.update({'cash_amount': self.maCash, 'stocks': None }, Trade.type == 'current_state')
        self.db.insert({'type': 'trade', 'stocks': [ {'stock': 'tvix', 'shares': n, 'price': stockPrice } ], 'transaction': transactionType })
        f = open("trading_log.txt", "a")
        f.write('<=================trade number %s===================' % self.tradeNumber)
        f.write('cash is %s' % self.maCash)
        # f.write('stocks value is %s' % self.maCash)
        f.write('bought %s tvix at %s' % (n, stockPrice))
        f.write('current price is %s' % self.last10TradesPrices[0].text)
        f.write('=====================================>')
        f.close()
        self.tradeNumber = self.tradeNumber + 1
            
if __name__ == "__main__":
    TRADER().__init__()
        