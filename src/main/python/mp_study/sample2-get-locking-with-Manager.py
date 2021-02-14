# -*- coding: utf-8 -*-
from multiprocessing import Pool, Manager, current_process, Lock
from datetime import datetime, timedelta
from time import sleep
import sys

def use_manage(first, lock):
    print(current_process())
    while True:
        lock.acquire()
        try:
            v = first.pop()
            print(v)
        except IndexError:
            #print("Exception1")
            #print(sys.exc_info()[0])
            lock.release()
            print("DEBUG: Lock released ")
            return
        finally:
            lock.release()


if __name__ == "__main__":
    manage = Manager()
    list1 = manage.list()
    print("Hello World")
    pool = Pool(4)
    a = list(range(100))
    for i in a:
        list1.append(i)
    lock = manage.Lock()
    for i in range(4):
        pool.apply_async(use_manage, args=(list1, lock,))
    pool.close()
    pool.join()
