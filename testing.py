# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 22:58:07 2019

@author: Ldeezy
"""

#import logging
#import threading
#import time
#from datetime import datetime
#import multiprocessing
#
#somevar = 'yo'
#
#def thread_function():
#    global somevar
#    print("Thread 1: starting")
#    time.sleep(2)
#    while True:
#        print('yo')
#        time.sleep(1)
#    logging.info("Thread 1: finishing")
#    
#def thread_function2():
#    global somevar
#    print("Thread 2: starting")
#    for i in range(15):
#        print(i)
#        if i == 10:
#            somevar = 'hey'
#    print("Thread 2: finishing")
#    
#def stopper(a, b):
#    while True:
#        print('still true')
#        if datetime.now().hour + datetime.now().minute > 62:
#            a.terminate()
#            b.terminate()
#            break
#        time.sleep(10)
#
#if __name__ == "__main__":
#    format = "%(asctime)s: %(message)s"
#    logging.basicConfig(format=format, level=logging.INFO,
#                        datefmt="%H:%M:%S")
#
#    logging.info("Main    : before creating thread")
#    x = threading.Thread(target=thread_function)
#    y = threading.Thread(target=thread_function2)
#    logging.info("Main    : before running thread")
#    x.start()
#    y.start()
#    logging.info("Main    : wait for the thread to finish")
#    # x.join()
#    logging.info("Main    : all done")
#    while True:
#        if datetime.now().hour + datetime.now().minute > 48:
#            print('terminating')
#            y.terminate()
#            x.terminate()
#            break
#        time.sleep(20)
        
#if __name__=='__main__':
#    jobs = []
#    a = multiprocessing.Process(target=thread_function())
#    b = multiprocessing.Process(target=thread_function2())
##    c = multiprocessing.Process(target=stopper(), args=(a,b))
#    jobs.append(a)
#    jobs.append(b)
##    jobs.append(c)
#    jobs.join()
#    a.start()
#    b.start()
##    c.start()
    
    
import multiprocessing
import time


def hang():
    while True:
        print('hanging..')
        time.sleep(1)


def main(p):
    
    time.sleep(10)
    p.terminate()
    p.join()
    print('main process exiting..')


if __name__ == '__main__':
    p = multiprocessing.Process(target=hang())
    p.start()
    b = multiprocessing.Process(target=main(p,))
    b.start()