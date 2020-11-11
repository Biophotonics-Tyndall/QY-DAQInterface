import time

import threading
t0 = time.time()

def a():
    while t0 + 0.0001 > time.time():
        pass
    print("Function a is running at time: " + str(time.time()) + " s.")
    # time.sleep(0.1)

def b():
    while t0 + 0.0001 > time.time():
        pass
    print("Function b is running at time: " + str(time.time()) + " s.")

if __name__=='__main__':
    threading.Thread(target=a).start()
    threading.Thread(target=b).start()
