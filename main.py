# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 13:40:37 2019

@author: Ldeezy
"""

import multiprocessing
import TRADER, ANALYZER


if __name__=='__main__':
    jobs = []
    a = multiprocessing.Process(target=ANALYZER.ANALYZER())
    b = multiprocessing.Process(target=TRADER.TRADER())
    jobs.append(a)
    jobs.append(b)
    a.start()
    b.start()




