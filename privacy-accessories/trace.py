"""
    Processes mitmdump requests into a shared queue

    Usage:
        mitmdump trace.py
"""

from multiprocessing.managers import BaseManager
import cgi
import urlparse
import pickle

BaseManager.register('get_queue')
m = BaseManager(address=('127.0.0.1', 50000), authkey='')
m.connect()
queue = m.get_queue()

def request(context, flow):
    serialized_request = pickle.dumps(flow.request)
    queue.put(serialized_request)

    """
    method = flow.request.method
    scheme = flow.request.scheme
    host = flow.request.host
    path = flow.request.path
    content = flow.request.content
    headers = flow.request.headers

    url = scheme + "://" + host + path
    url_data_dict = cgi.parse_qs(urlparse.urlparse(url).query)

    # go one level deeper for doubleclick data
    temp_url_data_dict = url_data_dict.copy()
    for key, value in url_data_dict.iteritems():
        try:
            if len(value) == 1:
                parsed = cgi.parse_qs(value[0])
                if parsed:
                    del temp_url_data_dict[key]
                    temp_url_data_dict.update(parsed)
        except:
            continue
    url_data_dict = temp_url_data_dict

    content_data_dict = cgi.parse_qs(content)

    if url_data_dict or content_data_dict:
        print "================= BEGIN ================="
        print host
        print url_data_dict
        print content_data_dict
        print "=================  END  ================="

        try:
            url_data_tosave = {unicode(key, "latin-1").encode('ascii', 'replace').replace('\x00', '').replace(".","").replace("$",""): [unicode(x, "latin-1").encode('ascii', 'replace') for x in value] for (key, value) in url_data_dict.items()}
        except:
            url_data_tosave = {}

        try:
            content_data_tosave = {unicode(key, "latin-1").encode('ascii', 'replace').replace('\x00', '').replace(".","").replace("$",""): [unicode(x, "latin-1").encode('ascii', 'replace') for x in value] for (key, value) in content_data_dict.items()}
        except:
            content_data_tosave = {}


        to_save = {
            "host" : host,
            "url_data" : url_data_tosave,
            "content_data" : content_data_tosave,
        }

        queue.put(to_save)
    """

