# -*- coding: utf-8 -*-
from multiprocessing import Pool, Manager
from datetime import datetime, timedelta


def use_manage(first):
    return first[0] * first[1]


def use_manage_startmap(first, second):
    return first * second


if __name__ == "__main__":
    print("Hello World")
    a = range(10000)
    b = [(1, 2), (3, 4)]
    before = datetime.now()
    x = Pool().map(use_manage, b)
    y = Pool().starmap(use_manage_startmap, b)
    print(x)
    print(y)
    after = datetime.now()
    print(after - before)
