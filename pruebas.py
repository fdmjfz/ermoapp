import threading
import time


def myfun():
    print("HAHAH")
    time.sleep(2)


a = threading.Thread(target=myfun, name='jeje')
a.start()
