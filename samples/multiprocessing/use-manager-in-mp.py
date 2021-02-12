from multiprocessing import Pool, Process, Manager, Value

manager = Manager()
list_one = manager.list()

if __name__ == "__main__":
    a = list(range(10))

    def handle_function(i):
        list_one.append(i*i)

    pool = Pool()
    pool.map(handle_function, a)
    print(list_one)
    print("hello, World")