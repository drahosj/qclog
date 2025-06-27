#! /usr/bin/env python

import Hamlib

class Rig:
    def __init__(self, model, port, baud, opts={}):
        # Bring in mandator args
        conf = {}
        conf['rig_pathname'] = port
        conf['serial_speed'] = str(baud)

        # Set sane defaults
        conf['data_bits'] = '8'
        conf['stop_bits'] = '1'
        conf['serial_parity'] = 'None'
        conf['serial_handshake'] = 'None'
        conf['rts_state'] = 'OFF'
        conf['dtr_state'] = 'OFF'

        conf.update(opts)
        self.conf = conf
        self.model = model

    def start(self):
        r = Hamlib.Rig(self.model)
        if r.this is None:
            raise Exception("Invalid rig model")

        for k, v in self.conf.items():
            print(f"Setting conf {k} {v}")
            r.set_conf(k, v)

        if r.error_status:
            raise Exception(Hamlib.rigerror2(r.error_state))

        r.open()
        
        self.rig = r
        print("rig started")

    def get_freq(self):
        f = int(self.rig.get_freq())
        print(f"get_freq{f}")
        return f

    def get_mode(self):
        return mode_map[self.rig.get_mode()[0]]

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


mode_map = {getattr(Hamlib, x): x.split('_')[-1]
            for x in dir(Hamlib) 
            if x.startswith('RIG_MODE_')}
