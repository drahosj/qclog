#! /usr/bin/env python

import Hamlib

class Rig:
    def __init__(self, model, port, baud=38400, data_bits=8, stop_bits=1,
                 parity='None', 
                 handshake='None'):
        r = Hamlib.Rig(model)
        if r.this is None:
            raise Exception("Invalid rig model")

        r.set_conf('rig_pathname', port)
        r.set_conf('serial_speed', str(baud))
        r.set_conf('data_bits', str(data_bits))
        r.set_conf('stop_bits', str(stop_bits))
        r.set_conf('serial_parity', str(parity))
        r.set_conf('serial_handshake', str(handshake))

        r.open()

        if r.error_status:
            raise Exception(Hamlib.rigerror2(r.error_state))
        self.rig = r

    def get_freq(self):
        return int(self.rig.get_freq())

    def get_mode(self):
        return mode_map[self.rig.get_mode()[0]]

    def get_band(self):
        f = self.get_freq()
        # Hardcode for now
        if f in range(1800000, 2000001):
            return "160M"
        elif f in range(3500000, 4000001):
            return "80M"
        elif f in range(7000000, 7000301):
            return "40M"
        elif f in range(14000000, 14000351):
            return "20M"
        elif f in range(21000000, 21000451):
            return "15M"
        elif f in range(28000000, 29700001):
            return "10M"
        elif f in range(50000000, 54000001):
            return "6M"
        elif f in range(144000000, 148000001):
            return "2M"
        else:
            return "?BAND"


mode_map = {getattr(Hamlib, x): x.split('_')[-1]
            for x in dir(Hamlib) 
            if x.startswith('RIG_MODE_')}
