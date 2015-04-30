"""
    Daemon that manages a shared queue to push request data
    from mitmdump to chimp
"""

from multiprocessing.managers import BaseManager
import Queue

queue = Queue.Queue()
BaseManager.register('get_queue', callable=lambda:queue)
m = BaseManager(address=('', 50000), authkey="")
s = m.get_server()
s.serve_forever()