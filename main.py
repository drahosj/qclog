#! /usr/bin/env python3

# This Python file uses the following encoding: utf-8
import sys
import argparse
import os
import uuid
import random

from pathlib import Path

from PySide6.QtCore import QObject, Property, QTimer, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

import qclog.fldigi
import qclog.logger
import qclog.flrig
import qclog.net

from fldigiwrapper import FldigiWrapper
from rigwrapper import RigWrapper
from logwrapper import LoggerWrapper


class QCLog(QObject):
    testQso = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = None
        self.station_id = ""
        self.station_name = ""
        self.local_qso_count = 0

    def getStationId(self):
        return self.station_id

    def getStationName(self):
        return self.station_name

    def setStationId(self, station_id):
        self.station_id = station_id

    def setStationName(self, station_name):
        self.station_name = station_name

    def getLocalQsoCount(self):
        return self.logger.logger.local_count()

    @Slot()
    def makeTestQso(self):
        if random.randint(0, 4) != 0:
            return

        prefixes = ['ad', 'w', 'wn', 'n', 'ke', 'kd', 'kf']
        n = str(random.randint(0, 9))
        suffix = ''
        for i in range(random.randint(1, 3)):
            suffix += chr(random.randint(0x41, 0x5a))
        call = random.choice(prefixes) + n + suffix
        print(f"Firing off a test QSO: {call}")
        self.testQso.emit(call, {})

    stationId = Property(str, getStationId, setStationId)
    stationName = Property(str, getStationName, setStationName)


if __name__ == "__main__":
    if 'XDG_DATA_HOME' in os.environ:
        default_datadir = os.environ['XDG_DATA_HOME']
    else:
        default_datadir = Path(os.path.expanduser('~')) / '.local/share/qclog'

    parser = argparse.ArgumentParser()
    parser.add_argument('log', help='Name of database and log files',
                        default='qclog-defaultlog')
    parser.add_argument('-i', '--interface', default='fd')
    parser.add_argument('-o', '--operator')
    parser.add_argument('-b', '--band')
    parser.add_argument('-m', '--mode')
    parser.add_argument('-f', '--frequency')
    parser.add_argument('-n', '--station-name')
    parser.add_argument('--flrig',
                        help='Enable flrig to populate rig data',
                        action='store_true')
    parser.add_argument('--fldigi',
                        help='Automatically populate callsign from fldigi',
                        action='store_true')
    parser.add_argument('-d', '--data-dir', help='Directory for logs and db',
                        default=default_datadir)
    parser.add_argument('--hamlib',
                        help='Enable hamlib <model,port,baud>[,hamlib_opt...]')
    parser.add_argument('--rigctld', help='Connect to local rigctld on <port>')
    parser.add_argument('--test', action='store_true',
                        help='Enable test mode (generates qsos)')

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
    logger.qsoLogged.connect(root.localLogged)

    if args.flrig:
        rig = RigWrapper(qclog.flrig.Rig())
        context.setContextProperty("rig", rig)
        rig.updatedRigData.connect(root.populateRigData)
        rig.setStatus.connect(root.setStatus)
        rig.clearStatus.connect(root.clearStatus)
    elif args.hamlib is not None:
        import qclog.hamlib
        hamlib_args = args.hamlib.split(',')
        if len(hamlib_args) < 3:
            print("--hamlib requires at least model,ttypath,baud")
            sys.exit(-1)
        m = int(hamlib_args.pop(0))
        p = hamlib_args.pop(0)
        b = hamlib_args.pop(0)
        conf = {}
        for arg in hamlib_args:
            k, v = arg.split("=")
            conf[k] = v

        rig = RigWrapper(qclog.hamlib.Rig(m, p, b, conf))
        rig.updatedRigData.connect(root.populateRigData)
        rig.setStatus.connect(root.setStatus)
        rig.clearStatus.connect(root.clearStatus)
    elif args.rigctld is not None:
        import qclog.rigctld
        rig = RigWrapper(qclog.rigctld.Rig(int(args.rigctld)))
        rig.updatedRigData.connect(root.populateRigData)
        rig.setStatus.connect(root.setStatus)
        rig.clearStatus.connect(root.clearStatus)
    else:
        root.populateRigData(args.band, args.mode, args.frequency)

    if args.fldigi:
        fldigi = FldigiWrapper(qclog.fldigi.Fldigi())
        fldigi.logCallChanged.connect(root.setCall)

    _qclog = QCLog()

    _qclog.station_id = logger.logger.get_setting("station_id")
    if _qclog.station_id is None:
        print("No station id found, generating...")
        _qclog.station_id = str(uuid.uuid4())
        logger.logger.set_setting("station_id", _qclog.station_id)

    print(f"Station ID: {_qclog.station_id}")

    if args.station_name is not None:
        logger.logger.set_setting("station_name", args.station_name)

    logger.meta.update({"station_id": _qclog.station_id})
    _qclog.logger = logger

    _qclog.station_name = logger.logger.get_setting("station_name")
    if _qclog.station_name is None:
        _qclog.station_name = _qclog.station_id

    net_func = qclog.net.NetFunctions(_qclog)
    net_func.start_listener()
    net_func.enable_heartbeat()
    net_func.send_heartbeat()
    logger.qsoLogged.connect(net_func.send_qso)
    net_func.remoteQsoReceived.connect(logger.log_remote)
    net_func.remoteQsoReceived.connect(root.remoteLogged)
    context.setContextProperty('net', net_func)
    context.setContextProperty('qclog', _qclog)

    if args.test:
        test_timer = QTimer(_qclog)
        test_timer.timeout.connect(_qclog.makeTestQso)
        _qclog.testQso.connect(root.injectTestQso)
        test_timer.start(2000)

    root.setup(args.operator)
    root.updateTitleStatus()
    sys.exit(app.exec())
