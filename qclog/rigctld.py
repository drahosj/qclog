#! /usr/bin/env python

import socket

from qclog.flrig import RigCommError

class Rig:
    def __init__(self, port):
        # Bring in mandator args
        self.port = port

    def start(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(('localhost', self.port))

        print("rigctld started")

    def get_freq(self):
        self.s.send("f\n".encode())
        resp = self.s.recv(4096).decode()
        return int(resp)


    def get_mode(self):
        self.s.send("m\n".encode())
        resp = self.s.recv(4096).decode()
        return resp.splitlines(keepends=False)[0]


    def get_band(self):
        f = self.get_freq()
        # Hardcode for now
        if f in range(1800000, 2000001):
            return "160M"
        elif f in range(3500000, 4000001):
            return "80M"
        elif f in range(7000000, 7301000):
            return "40M"
        elif f in range(14000000, 14351000):
            return "20M"
        elif f in range(21000000, 21451000):
            return "15M"
        elif f in range(28000000, 29700001):
            return "10M"
        elif f in range(50000000, 54000001):
            return "6M"
        elif f in range(144000000, 148000001):
            return "2M"
        else:
            return "?BAND"

