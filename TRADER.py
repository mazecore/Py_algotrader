# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 19:57:19 2019

@author: Ldeezy
"""
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

import requests
import matplotlib.pyplot as plt
import numpy
import pandas as pd  
from math import *
import time, datetime
import threading


class TRADER:
    
    def __init__(self):
        print(str(datetime.datetime.now()).split('.')[0])
        self.browser = webdriver.Chrome('C:\chromedriver')
        # self.bidsAreHigh = false
        self.maCash = 25000
        self.url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?symbol=%5EGSPC&period1={}&period2={}&interval={}&includePrePost=true&events=div%7Csplit%7Cearn&lang=en-US&region=US&crumb=ED2zlWJHcMa&corsDomain=finance.yahoo.com"
        self.browser.get('http://markets.cboe.com/us/equities/market_statistics/book_viewer/')
        self.limit_order_pending = False
        self.stock_purchased = False

    def getYahooData(self):
        now = str(time.time()).split('.')[0]
        print(now)
        r = requests.get(self.url.format('1574186393', now, '30m'))
        yahoo = r.json()
        times = yahoo["chart"]["result"][0]["timestamp"]
        quote = yahoo["chart"]["result"][0]["indicators"]["quote"][0]
        # intialise data of lists. 
        data = {'Open': quote['open'] , 
                'Low': quote['low'] , 
                'High': quote['high'], 
                'Close': quote['close'],
                'Volume': quote['volume'],
                'Timestamp': times }
        df = pd.DataFrame(data) 
        self.moneyFlow = self.MFI(df, 14)
        
    def changeStock(self, stock):
        inputt = self.browser.find_element_by_xpath('//*[@id="symbol0"]')
        actions = ActionChains(self.browser)
        actions.move_to_element(inputt)
        actions.double_click(inputt)
        actions.send_keys(Keys.BACKSPACE)
        actions.send_keys(stock)
        actions.send_keys(Keys.ENTER)
        actions.perform()

    def MFI(df, n):
        """
        Money Flow Index and Ratio
        """
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
        if self.last10TradesPrices[0].text > price:
            self.limit_order_pending = True
        else:
            self.buy(price, n)
            self.stock_purchased = True
            
            
    def buy(self, stockPrice, n):
    #     getAmount
    #     subtract
    #     keep the amount as a sum of stock value and the remaining cash
        stocksValue = stockPrice * n
        self.maCash = self.maCash - stocksValue
        

    def check_stock_info(self):
        if not self.limit_order_pending or not self.stock_purchased:
            i = 0
            for j in self.topBidShares:
                if j.text > 1600:
                    self.set_limit_order(self.topBidsPrice[i].text, 500)
                    i = i + 1
                    

    def get_info_table(self):
        self.last10TradesPrices = self.browser.find_elements_by_class_name("book-viewer__trades-price")
        self.topBidsPrice = self.browser.find_elements_by_class_name("book-viewer__bid-price")
        self.topBidShares = self.browser.find_elements_by_class_name("book-viewer__bid-shares")
        self.topAskPrice = self.browser.find_elements_by_class_name("book-viewer__ask-price")
        self.topAskShares = self.browser.find_elements_by_class_name("book-viewer__ask-shares")
        # button = browser.find_element_by_xpath('//button[text()="I agree"]')
        # actions = ActionChains(browser)
        # actions.pause(1)
    #     actions.move_to_element(button)
        # print(button)
    #     actions.click(button)
        # actions.pause(1)
        # actions.perform()
        # bookRaw = browser.find_element_by_xpath('//*[@id="bookViewer0"]/div[1]/table[2]/tbody')
        
    #     shares = 
        # book = bookRaw.get_attribute('innerHTML')
        # bookSoup = BeautifulSoup(book, 'lxml').html.body
        # print(price)
        # print('book ===============>', book)
        # print('bookSoup ===============>', bookSoup)

    def set_interval(self):
        while True:
            time.sleep(1)
            self.check_stock_info()
            
if __name__ == "__main__":
    TRADER().__init__()
        