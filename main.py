# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 13:40:37 2019

@author: Ldeezy
"""

import multiprocessing
import TRADER, SP500


if __name__=='__main__':
    jobs = []
    a = multiprocessing.Process(target=SP500.SP500_ANALYZER('%5EGSPC'))
    b = multiprocessing.Process(target=TRADER.TRADER())
    jobs.append(a)
    jobs.append(b)
    a.start()
    b.start()




