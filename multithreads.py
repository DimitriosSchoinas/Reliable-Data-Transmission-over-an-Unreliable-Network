import logging
import threading
import time

def thread_fun(name):
    logging.info("Thread %s: starting", name)
    logging.info("Thread %s: do something that takes a little while...",name)
    time.sleep(10)
    logging.info("Thread %s: finishing", name)

if __name__ == "__main__":

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    logging.info("Main    : before creating thread")    
    logging.info("Main    : before creating thread")
    x = threading.Thread(target=thread_fun, args=(1,))
    logging.info("Main    : before running thread")
    x.start()
    logging.info("Main    : wait for the thread to finish")
#    x.join()
    logging.info("Main    : all done")
    
