# -*- coding: utf-8 -*-
from multiprocessing import Pool, Manager, current_process, Lock
from datetime import datetime, timedelta
from time import sleep
import sys
from functools import partial

# Reference
#   : https://stackoverflow.com/questions/25557686/python-sharing-a-lock-between-processes
#   : https://docs.python.org/3/library/functools.html#functools.partial


def use_manage(lock, list2, first):
    print(current_process())
    try:
        #v = first.pop()
        # print(v)
        lock.acquire()
        list2.append(first*first)
    except IndexError:
        # print("Exception1")
        # print(sys.exc_info()[0])
        lock.release()
        print("DEBUG: Lock released ")
        return
    finally:
        lock.release()


if __name__ == "__main__":
    manage = Manager()
    list1 = manage.list()
    list2 = manage.list()
    print("Hello World")
    pool = Pool(4)
    a = list(range(5))
    for i in a:
        list1.append(i)
    lock = manage.Lock()
    pool.map(partial(use_manage, lock, list2), list1)
    pool.close()
    pool.join()
    print(list2)
