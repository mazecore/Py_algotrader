# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 19:57:19 2019

@author: Ldeezy
"""
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import time
from datetime import datetime, date
from tinydb import TinyDB, Query
import sys


class TRADER:
    
    def __init__(self):
        print(str(datetime.now()).split('.')[0])
        self.browser = webdriver.Chrome('C:\chromedriver')
        self.browser.get('http://markets.cboe.com/us/equities/market_statistics/book_viewer/')
        self.limit_order_pending = False
        self.stock_purchased = False
        self.stock_sold = False
        self.db = TinyDB('DB.json', sort_keys=True, indent=4, separators=(',', ': '))
        print('database length', len(self.db))
        print('last record: ', self.db.get(doc_id=len(self.db)))
        last_trade = (self.db.search(Query().type == 'trade'))[-1]
        print('last trade ======> ', last_trade)
        current_state = (self.db.search(Query().type == 'current_state'))[0]
        self.maCash = current_state['cash_amount']

#        if (self.db.search(record.type == 'current_state'))[0]['limit_order_pending'] == True:
        if current_state['five_hour_pending'] > 0 and last_trade['transaction'] == 'purchase':
            print('There is a stock that needs to be sold.')
            self.fiveHourPending = current_state['five_hour_pending']
            self.limit_order_pending = True        
            self.stock_purchased = True
        else:
            self.fiveHourPending = 0

        print('ma cash: ', self.maCash)
        self.tradeNumber = 0
        self.attempt = 0
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
        self.register_the_trade(n, price, transaction)
        
        oneMinTimer = time.time() + 240
        if transaction == 'purchase':
            while self.stock_purchased == False:
                self.buy(price, n)
                time.sleep(1)
                if time.time() > oneMinTimer:
                    print('4 minutes elapsed. Limit order cancelled.')
                    self.limit_order_pending = False
                    break
        else:
            while self.stock_sold == False:
                self.sell(price, n)
                time.sleep(1)
                if time.time() > oneMinTimer:
                    print('4 minutes elapsed. Limit order cancelled.')
                    self.limit_order_pending = False
                    break


    def buy(self, stockPrice, n):
        self.currentPrice = float(self.last10TradesPrices[0].text)
        print('Trying to buy at %s. Current price is: %s' % (stockPrice, self.currentPrice))
        if self.currentPrice <= stockPrice:
            self.maCash = self.maCash - stockPrice * n
            self.stock_purchased = True
            self.limit_order_pending = False
            self.set_five_hour_timestamp()
            self.register_the_trade(n, stockPrice, 'purchase')
            print('\n B O U G H T  at   %s \n' % stockPrice)
            self.monitor_for_5hours_until_1percent_is_gained()
        
    def sell(self, stockPrice, n):
        self.currentPrice = float(self.last10TradesPrices[0].text)
        print('Trying to sell at %s. Current price is: %s' % (stockPrice, self.currentPrice))
        if self.currentPrice >= stockPrice:
            self.maCash = self.maCash + stockPrice * n
            self.stock_sold = True
            self.stock_purchased = False
            self.limit_order_pending = False
            self.fiveHourPending = 0
            self.register_the_trade(n, stockPrice, 'sale')
            print('\n S O L D   at   %s \n' % stockPrice)
            

    def set_five_hour_timestamp(self):
        print('setting five hour timestamp...')
        today = [ datetime.now().year, datetime.now().month, datetime.now().day ]
        timestamp_now = time.time()
        
        if datetime.now().hour < 16:
            deltaTillClose = datetime(*today, 16,0) - datetime.now()
            print('{} minutes till close.'.format(deltaTillClose.seconds/60))
            if deltaTillClose.seconds < 18000:
                if date(*today).weekday() == 4:
                    self.fiveHourPending = timestamp_now + 253800
                    print('five hour deadline set for Monday at ', datetime.fromtimestamp(self.fiveHourPending))
                else:
                    self.fiveHourPending = timestamp_now + 81000
                    print('five hour deadline set for tomorrow at ', datetime.fromtimestamp(self.fiveHourPending))
            else:
                self.fiveHourPending = timestamp_now + 18000
                print('five hour deadline set for today at ', datetime.fromtimestamp(self.fiveHourPending))
        else:
            deltaTill8pm = (datetime(*today, 20,0) - datetime.now()).seconds
            self.fiveHourPending = timestamp_now + 66600 + deltaTill8pm
            print('five hour deadline set for tomorrow at ', datetime.fromtimestamp(self.fiveHourPending))
            if date(*today).weekday() == 4:
                self.fiveHourPending = timestamp_now + 239400 + deltaTill8pm
                print('five hour deadline set for Monday at ', datetime.fromtimestamp(self.fiveHourPending))
            


    def check_against_EDGX_bids(self):
        print('checking against EDGX bids...')
        try:
            if self.stock_purchased == False:
                i = 0
                for j in self.topBidShares:
                    if int((j.text).replace(',','')) >= 2000:
                        print('A %s share -BID- detected. Placing a buy limit order for tvix at %s' % (self.topBidShares[i].text, float(self.topBidsPrice[i].text)))
                        fiveMinMF = (self.db.search(Query().type == 'current_state'))[0]['SP500_5mMF']['value']
                        if fiveMinMF:
                            if fiveMinMF > 0.7:
                                self.set_limit_order(float(self.topBidsPrice[i].text), 100, 'purchase')
                                break
                        # set shares amount equal to a percentage of portfolio
                        self.set_limit_order(float(self.topBidsPrice[i].text), 50, 'purchase')
                        break
                    i = i + 1
            else:
                b = 0
                for s in self.topAskShares:
                    if int((s.text).replace(',','')) >= 2000:
                        price = (self.db.search(Query().type == 'trade'))[-1]['stock']['price']
                        if price + price * 0.01 < float(self.topAskPrice[b].text):
                            print('A 2000 share -ASK- detected. Placing a sale limit order for tvix at %s' % float(self.topAskPrice[b].text))
                            self.set_limit_order(float(self.topAskPrice[b].text), 50, 'sale')
                            break
                    b = b + 1
        except Exception as e:
            print('exception', e)
            if self.attempt > 2:
                self.db.update({'afterhours': True, 
                            }, Query().type == 'current_state')
                sys.exit('No bids or asks. Arrivederci...')
            self.attempt += 1
            print('attempting again... attempt number ', self.attempt)


    def check_5min_MF(self):
        print('checking 5 minute Money Flow...')
        try:
            fiveMinMF = (self.db.search(Query().type == 'current_state'))[0]['SP500_5mMF']['value']
            print('5 minute Money Flow is %s.' % fiveMinMF)
            if fiveMinMF:
                if fiveMinMF > 0.76:
                    if self.stock_purchased == False:
                        # add control for momentum. Momentum shouldn't be higher than 16
                        self.buy(self.currentPrice, 100)
                if fiveMinMF < 0.3:
                    if self.stock_purchased == True:
                        record = Query()
                        last_record = (self.db.search(record.type == 'trade'))[-1]
                        if last_record['price'] + last_record['price'] * 0.01 < self.currentPrice:
                           self.sell(self.currentPrice, 50)
        except:
            print('No 5 minute Money Flow data')
            

    def monitor_for_5hours_until_1percent_is_gained(self):
        print('setting monitoring. five hour deadline : ', datetime.fromtimestamp(self.fiveHourPending))
        print('monitoring for 5 hours. %s minutes left till deadline.' % str(round((self.fiveHourPending - time.time()) / 60)))
        sleepTime = 10
        last_record = (self.db.search(Query().type == 'trade'))[-1]['stock']
        target_price = last_record['price'] + last_record['price'] * 0.01
        while  self.stock_purchased == True:
            if time.time() < self.fiveHourPending:
                self.currentPrice = float(self.last10TradesPrices[0].text)
                if self.currentPrice > target_price - target_price * 0.006:
                    sleepTime = 1
                else:
                    sleepTime = 10
                print('monitoring for 5 hours... trying to sell at %s. And current price is: %s ' % (target_price, self.currentPrice))

                print('profit : {}'.format(last_record['shares'] * self.currentPrice - last_record['shares']* last_record['price']))
                print('target profit: {}'.format(last_record['shares'] * target_price - last_record['shares']* last_record['price']))
                
                # consider not selling if MF is above .7. Wait till the MF starts to turn downward.
                # consider adding a 20 day moving average on 2 min frequency as a possible spot for short term (mostly) or 
                # maybe even long term (if it's close enough to the 0.001 % target) sell target
                if target_price < self.currentPrice:
                   self.sell(self.currentPrice, last_record['shares'])
                   break
                if self.currentPrice < last_record['price'] - last_record['price'] * 0.03:
                    print('S T O P  L O S S triggered...')
                    self.sell(self.currentPrice, last_record['shares'])
                    break
                time.sleep(sleepTime)
            else:
                # self.reevaluate_state()
                self.sell(self.currentPrice, last_record['shares']) # temporary solution
                print('five hour wait was fruitless...')
                break
            self.check_time_of_day()

    def reevaluate_state(self):
        # if 30m money flow and 4hr money flow is descending then hold 5 hours more
        fiveMinMF = (self.db.search(Query().type == 'current_state'))[0]['SP500_5mMF']
        thirtyMinMF = (self.db.search(Query().type == 'current_state'))[0]['SP500_30mMF']
        print('is current 30min MF descending? = ', thirtyMinMF['descending'])
        print('is current 5min MF descending? = ', fiveMinMF['descending'])
        self.fiveHourPending = 0
        self.db.update({ 'five_hour_pending': self.fiveHourPending }, Query().type == 'current_state')
        # self.limit_order_pending = False  ?
        # distinguish between 5m moneyflow strategy and level II strategy maybe. Probably not. 
        # combine the strategies for a very good trade ( possibly large number of shares ) 
        # alternatively let separate strategies go for a very short term shot
        # reevaluate situation and either extend the wait or find the best timing to sell or sell immediately
    
    def check_time_of_day(self):
        if datetime.now().hour > 20:
            self.db.update({'afterhours': True, 
                            }, Query().type == 'current_state')
            sys.exit('8 pm. Arrivederci...')

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
            print(self.currentPrice)
            if self.limit_order_pending == False:
                self.check_5min_MF()
                self.check_against_EDGX_bids()
            else: 
                self.monitor_for_5hours_until_1percent_is_gained()

    def register_the_trade(self, n, stockPrice, transactionType):
        print('registering the trade')
        print('cash_amount:', self.maCash)
        profit = None
        portfolio_value = self.maCash
        f = open("trading_log.txt", "a")
        f.write('\n---%s---\n' % str(datetime.now()))
        if self.limit_order_pending:
            self.db.update({'cash_amount': self.maCash,
                        'portfolio_value': self.maCash,
                        'five_hour_pending': self.fiveHourPending
                        }, Query().type == 'current_state')
            f.write('<==={ trade number %s }==\n' % self.tradeNumber)
            f.write('only limit order \n')
            
        else:
            f.write('<================={ trade number %s }===================\n' % self.tradeNumber)
            if transactionType == 'purchase':
                portfolio_value = self.maCash + stockPrice * n
                self.db.update({'cash_amount': self.maCash, 
                            'last_closed_trade': transactionType,
                            'portfolio_value': portfolio_value,
                            'five_hour_pending': self.fiveHourPending
                            }, Query().type == 'current_state')
                f.write('five hour deadline: %s \n' % datetime.fromtimestamp(self.fiveHourPending))
            else:
                self.db.update({'cash_amount': self.maCash, 
                            'last_closed_trade': transactionType,
                            'portfolio_value': portfolio_value,
                            'five_hour_pending': self.fiveHourPending
                            }, Query().type == 'current_state')
    
        f.write('cash is %s \n' % self.maCash)
        f.write('portfolio value is %s \n' % portfolio_value)
        f.write('--%s-- %s tvix at %s \n' % (transactionType.upper(), n, stockPrice))
        f.write('current price is %s \n' % self.last10TradesPrices[0].text)
        

        if self.limit_order_pending:
            f.write('==================>\n')
            self.db.insert({'type':'attempt', 
                            'date': str(datetime.now()),
                            'stock': {'name': 'tvix', 'shares': n, 'price': stockPrice }, 
                            'transaction': transactionType,
                            'profit': profit,
                           })
        else:
            if transactionType == 'sale':
               prices = (self.db.search(Query().type == 'trade'))
               purchasePrices = list(filter(lambda x: x['transaction'] == 'purchase', prices))
               profit = n * stockPrice - n* purchasePrices[-1]['stock']['price']
               f.write('profit : {} \n'.format(profit))
        
            f.write('=======================================================>\n')
            
            self.db.insert({'type':'trade', 
                            'date': str(datetime.now()),
                            'stock': {'name': 'tvix', 'shares': n, 'price': stockPrice }, 
                            'transaction': transactionType,
                            'profit': profit,
                           })
        f.close()
        

        self.tradeNumber = self.tradeNumber + 1


        

        