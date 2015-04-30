
import logging

logging.basicConfig(format='%(message)s', level=logging.DEBUG, filename='runs.log')

def log(message):
    logging.info(message)

def clear_queue(queue):
    while not queue.empty():
        queue.get()
