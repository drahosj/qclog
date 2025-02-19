#! /usr/bin/env python

import xmlrpc.client

class Rig:
    def __init__(self, host='127.0.0.01', port='12345'):
        self.server = xmlrpc.client.ServerProxy(f"http://%s:%s" % (host, port))

    def get_freq(self):
        try:
            print("Updating frequency from rig")
            freq =  int(self.server.rig.get_vfoA())
            print("Got frequency: ", freq)
            return(freq)
        except ConnectionRefusedError as e:
            raise RigCommError

    def get_mode(self):
        return self.server.rig.get_mode()

    def get_band(self):
        f = self.get_freq()
        # Hardcode for now
        if f in range(1800000, 2000001):
            return "160M"
        elif f in range(3500000, 4000001):
            return "80M"
        elif f in range(7000000, 7300001):
            return "40M"
        elif f in range(14000000, 14350001):
            return "20M"
        elif f in range(21000000, 21450001):
            return "15M"
        elif f in range(28000000, 29700001):
            return "10M"
        elif f in range(50000000, 54000001):
            return "6M"
        elif f in range(144000000, 148000001):
            return "2M"
        else:
            return "?BAND"

class RigCommError(Exception):
    pass
