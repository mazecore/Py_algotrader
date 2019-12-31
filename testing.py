# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 22:58:07 2019

@author: Ldeezy
"""

import threading, time
def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class MyClass:
#     somevar = 'someval'
    def __init__(self):
       self.somevar = 'someval'
       t1 = threading.Thread(target=self.func_to_be_threaded())
       t2 = threading.Thread(target=self.loop())
       t2.start()
       t1.start()
       t2.join()
       t1.join()

    def func_to_be_threaded(self):
        while self.somevar == 'someval':
            print('yo')
            time.sleep(3)
            

    def loop(self):
        for i in 100:
           print('hey', i)
           if i == 30:
              self.somevar = 'drrr'
            
    
MyClass().__init__()