#! /usr/bin/env python

import xmlrpc.client

class Fldigi:
    def __init__(self, host='127.0.0.01', port='7362'):
        self.server = xmlrpc.client.ServerProxy(f"http://%s:%s" % (host, port))

    def get_call(self):
        try:
            return self.server.log.get_call()
        except ConnectionRefusedError as e:
            raise FldigiCommError
        

class FldigiCommError(Exception):
    pass
