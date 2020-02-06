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
from threading import Thread



class TRADER:
    
    def __init__(self):
        print(str(datetime.now()).split('.')[0])
        self.browser = webdriver.Chrome('C:\chromedriver')
        self.browser.get('http://markets.cboe.com/us/equities/market_statistics/book_viewer/')
        self.limit_order_pending = False
        self.stock_purchased = False
        self.stock_sold = False
        self.db = TinyDB('DB.json')
        record = Query()
        self.maCash = (self.db.search(record.type == 'current_state'))[0]['cash_amount']
        print(self.maCash)
        self.tradeNumber = 0
        self.change_Stock_and_go_to_EDGX('TVIX')
        
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


    def set_limit_order(self, price, n, transaction):
        print('setting limit order')
        # register rate of change on the minute range
        # if tvix rate of change goes up, cancel tvix purchase
        # and if tvix rate of change goes down, cancel tvix limit order sale.. maybe idk
        self.limit_order_pending = True
        oneMinTimer = time.time() + 60
        if transaction == 'purchase':
            while self.stock_purchased == False:
                self.buy(price, n)
                time.sleep(1)
                if time.time() < oneMinTimer:
                    break
        else:
            while self.stock_sold == False:
                self.sell(price, n)
        
            
    def buy(self, stockPrice, n):
        print('buying')
        if self.currentPrice <= stockPrice:
            self.maCash = self.maCash - stockPrice * n
            print('bought at %s' % stockPrice)
            self.stock_purchased = True
            self.limit_order_pending = False
            self.register_the_trade(n, stockPrice, 'purchase')
            print('bought')
        
    def sell(self, stockPrice, n):
        print('selling')
        if self.currentPrice >= stockPrice:
            self.maCash = self.maCash + stockPrice * n
            print('sold at %s' % stockPrice)
            self.stock_sold = True
            self.stock_purchased = False
            self.limit_order_pending = False
            self.register_the_trade(n, stockPrice, 'sale')
            print('sold')


    def check_against_EDGX_bids(self):
        print(self.currentPrice)
        if self.stock_purchased == False:
            i = 0
            for j in self.topBidShares:
                if int((j.text).replace(',','')) >= 500:
                    print('A 500 share bid detected. Placing a buy limit order for tvix at %s' % float(self.topBidsPrice[i].text))
                    self.set_limit_order(float(self.topBidsPrice[i].text), 50, 'purchase')
                    break
                i = i + 1
        else:
            b = 0
            for s in self.topAskShares:
                if int((s.text).replace(',','')) >= 500:
                    print('A 500 share ask detected. Placing a sale limit order for tvix at %s' % float(self.topAskPrice[b].text))
                    self.set_limit_order(float(self.topAskPrice[b].text), 50, 'sale')
                    break
                b = b + 1
                
    def check_5min_MF(self):
        try:
            record = Query()
            fiveMinMF = (self.db.search(record.type == 'current_state'))[0]['SP500_5mMF']
            if fiveMinMF > 0.76:
                # add control for momentum. Momentum shouldn't be higher than 16
                self.buy(self.currentPrice, 50)
                self.monitor_for_5hours_until_1percent_is_gained()
        except:
            print('no 5 min MF')
            
    def monitor_for_5hours_until_1percent_is_gained(self):
        self.fiveHoursIntoTheFuture = time.time() + 18000
        while time.time() < self.fiveHoursIntoTheFuture and self.stock_purchased == False:
            self.currentPrice = float(self.last10TradesPrices[0].text)
            Trade = Query()
            if self.db.search(Trade.type == 'trade')[0]['stocks'][0]['price'] * 0.01 >= self.currentPrice:
               self.sell(self.currentPrice, self.db.search(Trade.type == 'trade')[0]['stocks'][0]['shares'])
        

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
            self.currentPrice = float(self.last10TradesPrices[0].text)
            if self.limit_order_pending == False:
                self.check_5min_MF()
                self.check_against_EDGX_bids()
            
    def register_the_trade(self, n, stockPrice, transactionType):
        print('registering the trade')
        print('cash_amount:', self.maCash)
        Trade = Query()
        self.db.update({'cash_amount': self.maCash, 'stocks': None }, Trade.type == 'current_state')
        self.db.insert({'type': 'trade', 'stocks': [ {'stock': 'tvix', 'shares': n, 'price': stockPrice } ], 'transaction': transactionType })
        f = open("trading_log.txt", "a")
        f.write('<=================trade number %s===================\n' % self.tradeNumber)
        f.write('cash is %s \n' % self.maCash)
        # f.write('stocks value is %s' % self.maCash)
        f.write('bought %s tvix at %s \n' % (n, stockPrice))
        f.write('current price is %s \n' % self.last10TradesPrices[0].text)
        f.write('=====================================>\n')
        f.close()
        self.tradeNumber = self.tradeNumber + 1
        

            
#if __name__ == "__main__":
#    print('trader name main')
#    TRADER().__init__()
        