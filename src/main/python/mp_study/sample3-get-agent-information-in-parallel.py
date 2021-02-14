# -*- coding: utf-8 -*-
from multiprocessing import Pool, Manager, current_process, Lock
from datetime import datetime, timedelta
from time import sleep
import sys
from functools import partial
import pandas as pd
import numpy as numpy
import argparse
from paramiko import SSHClient
import paramiko

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--input", required=True)
arg_parser.add_argument("--user", required=True)
arg_parser.add_argument("--password", required=True)
args = arg_parser.parse_args()

# Reference
#   : https://stackoverflow.com/questions/25557686/python-sharing-a-lock-between-processes
#   : https://docs.python.org/3/library/functools.html#functools.partial

def get_host_info(host_address):
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect(host_address, port=22, username=args.user, password=args.password)
    stdin, stdout, stderr = client.exec_command("nproc")
    nproc_value = stdout.read().decode("utf8").strip()
    client.close()
    return {"no_of_cores": nproc_value}

def use_manage(lock, list2, host_address):
    print("INFO: Handle " + host_address)
    try:
        nproc_value = get_host_info(host_address)['no_of_cores']
        lock.acquire()
        list2.append({"host_address": host_address, "no_of_cores": nproc_value})
    except RuntimeError:
        return 
    except NameError:
        return 
    except:
        lock.release()
        print("Exception1")
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
        print("DEBUG: Lock released ")
        return
    finally:
        lock.release()


if __name__ == "__main__":
    df = pd.read_excel(args.input)
    manage = Manager()
    list_input = manage.list()
    list_output = manage.list()
    print("Hello World")
    pool = Pool(4)
    a = list(range(5))
    for i in a:
        list_input.append(i)
    lock = manage.Lock()
    pool.map(partial(use_manage, lock, list_output), df['host'])
    pool.close()
    pool.join()
    for a in list_output:
        print(a)
