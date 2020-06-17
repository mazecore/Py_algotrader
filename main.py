# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 13:40:37 2019

@author: Ldeezy
"""

import multiprocessing
import TRADER, ANALYZER
#from datetime import datetime
#from time import sleep
#import sys
from tinydb import TinyDB, Query


if __name__=='__main__':
    db = TinyDB('DB.json', sort_keys=True, indent=4, separators=(',', ': '))
    db.update({'afterhours': False, 
               'SP500_5mMF': { 'value': None, 'descending': None },
               'SP500_5mROC': { 'value': None, 'descending': None },
               'SP500_30mMF': { 'value': None, 'descending': None }}, Query().type == 'current_state')
    analyzer = ANALYZER.ANALYZER()
    trader = TRADER.TRADER()
    jobs = []
    a = multiprocessing.Process(target=analyzer)
    b = multiprocessing.Process(target=trader)
    jobs.append(a)
    jobs.append(b)
    a.start()
    b.start()
#    sleep(10)
 #   a.terminate()
    a.join()
#    b.terminate()
    b.join()
#    while True:
#        print('still true')
#        sleep(5)
#        if datetime.now().hour + datetime.now().minute > 63:
#        # if datetime.now().hour + datetime.now().minute > 74:
#            print('terminating')
#            a.terminate()
#            b.terminate()
#            
#            
#            break
#        sleep(10)
            
 
# create a batch file that would monitor internet connection and restart wi-fi if necessary
# replace tinydb with sql-lite


