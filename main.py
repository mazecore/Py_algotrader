# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 13:40:37 2019

@author: Ldeezy
"""

import multiprocessing
import TRADER, ANALYZER
from datetime import datetime
from time import sleep
import sys
from tinydb import TinyDB, Query


if __name__=='__main__':
    db = TinyDB('DB.json')
    Trade = Query()
    db.update({'afterhours': False }, Trade.type == 'current_state')
    ANALYZER.ANALYZER()
    TRADER.TRADER()
#    sleep(10)
#    sys.exit()
#    analyzer = ANALYZER.ANALYZER()
#    trader = TRADER.TRADER()
#    jobs = []
#    a = multiprocessing.Process(target=analyzer)
#    b = multiprocessing.Process(target=trader)
#    jobs.append(a)
#    jobs.append(b)
#    a.start()
#    b.start()
##    sleep(10)
# #   a.terminate()
#    a.join()
##    b.terminate()
#    b.join()
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
            




