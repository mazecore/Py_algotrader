# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 22:58:07 2019

@author: Ldeezy
"""

import logging
import threading
import time

somevar = 'yo'

def thread_function():
    global somevar
    logging.info("Thread 1: starting")
    # time.sleep(2)
    while somevar == 'yo':
        print('yo')
        # time.sleep(1)
    logging.info("Thread 1: finishing")
    
def thread_function2():
    global somevar
    logging.info("Thread 2: starting")
    for i in range(15):
        print(i)
        if i == 10:
            somevar = 'hey'
    logging.info("Thread 2: finishing")

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("Main    : before creating thread")
    x = threading.Thread(target=thread_function)
    y = threading.Thread(target=thread_function2)
    logging.info("Main    : before running thread")
    x.start()
    y.start()
    logging.info("Main    : wait for the thread to finish")
    # x.join()
    logging.info("Main    : all done")