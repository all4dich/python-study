# -*- coding: utf-8 -*-
from multiprocessing import Pool, Manager, current_process, Lock
from datetime import datetime, timedelta
from time import sleep
import sys

# Reference
#   : https://stackoverflow.com/questions/25557686/python-sharing-a-lock-between-processes
#   : https://docs.python.org/3/library/functools.html#functools.partial


def use_manage(first):
    print(current_process())
    while True:
        try:
            lock.acquire()
            v = first.pop()
            print(v)
        except IndexError:
            # print("Exception1")
            # print(sys.exc_info()[0])
            print("DEBUG: Lock released ")
            return
        finally:
            lock.release()


def init_lock(l):
    global lock
    lock = l


if __name__ == "__main__":
    manage = Manager()
    list1 = manage.list()
    print("Hello World")
    a = list(range(10))
    for i in a:
        list1.append(i)
    l = Lock()
    pool = Pool(4, initializer=init_lock, initargs=(l,))
    for i in range(4):
        pool.apply_async(use_manage, args=(list1,))
    pool.close()
    pool.join()
