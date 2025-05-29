#! /usr/bin/env python3

# This Python file uses the following encoding: utf-8
import sys
import json
import argparse
import os
import uuid

from pathlib import Path

from PySide6.QtCore import Signal, QObject, Slot, QThread, Property, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement

import qclog.fldigi
import qclog.logger
import qclog.flrig
import qclog.net

from fldigiwrapper import FldigiWrapper
from rigwrapper import RigWrapper
from logwrapper import LoggerWrapper

class GlobalValues(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.station_id = ""
        self.station_name = ""
        
    def getStationId(self):
        return self.station_id
    
    def getStationName(self):
        return self.station_name
    
    def setStationId(self, station_id):
        self.station_id = station_id
        
    def setStationName(self, station_name):
        self.station_name = station_name
        
    stationId = Property(str, getStationId, setStationId)
    stationName = Property(str, getStationName, setStationName)

if __name__ == "__main__":
    default_datadir = Path(os.path.expanduser('~')) / '.qclog'

    parser = argparse.ArgumentParser()
    parser.add_argument('log', help='Name of database and log files',
                        default='qclog-defaultlog')
    parser.add_argument('-i', '--interface', default='fd')
    parser.add_argument('-o', '--operator')
    parser.add_argument('-b', '--band')
    parser.add_argument('-m', '--mode')
    parser.add_argument('-f', '--frequency')
    parser.add_argument('-n', '--station-name')
    parser.add_argument('--flrig', help='Enable flrig', action='store_true')
    parser.add_argument('--fldigi', help='Enable flrig', action='store_true')
    parser.add_argument('-d', '--data-dir', help='Directory for logs and db',
                        default=default_datadir)

    args = parser.parse_args(sys.argv[1:])

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    iface_dir =  Path(__file__).resolve().parent / "Interfaces"
    qml_file = iface_dir / f"{args.interface}.qml"
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)

    root = engine.rootObjects()[0]
    context = engine.rootContext()

    print(f"Storing logs in {args.data_dir}.")
    if not os.path.exists(args.data_dir):
        print(f"{args.data_dir} doesn't exist, creating.")
        os.makedirs(args.data_dir)

    logger = LoggerWrapper(qclog.logger.Logger(args.log, Path(args.data_dir)))
    context.setContextProperty("logger", logger)
    logger.setStatus.connect(root.setStatus)
    logger.clearStatus.connect(root.clearStatus)
    logger.logResponse.connect(root.logged)

    if args.flrig:
        rig = RigWrapper(qclog.flrig.Rig())
        context.setContextProperty("rig", rig)
        rig.updatedRigData.connect(root.populateRigData)
        rig.setStatus.connect(root.setStatus)
        rig.clearStatus.connect(root.clearStatus)
    else:
        root.populateRigData(args.band, args.mode, args.frequency)

    if args.fldigi:
        fldigi = FldigiWrapper(qclog.fldigi.Fldigi())
        fldigi.logCallChanged.connect(root.setCall)
        
    gv = GlobalValues()

    gv.station_id = logger.logger.get_setting("station_id")
    if gv.station_id is None:
        print("No station id found, generating...")
        gv.station_id = str(uuid.uuid4())
        logger.logger.set_setting("station_id", gv.station_id)

    print(f"Station ID: {gv.station_id}")
    
    if args.station_name is not None:
        logger.logger.set_setting("station_name", args.station_name)
        
    logger.meta.update({"station_id" : gv.station_id})
        
    gv.station_name = logger.logger.get_setting("station_name")
    if gv.station_name is None:
        gv.station_name = gv.station_id

    net_func = qclog.net.NetFunctions(gv)
    net_func.start_listener()
    net_func.enable_heartbeat()
    net_func.send_heartbeat()
    logger.qsoLogged.connect(net_func.send_qso)
    net_func.remoteQsoReceived.connect(logger.log_remote)
    

    root.setup(args.operator)
    sys.exit(app.exec())
