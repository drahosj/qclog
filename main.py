#! /usr/bin/env python3

# This Python file uses the following encoding: utf-8
import sys
import json
import argparse

from pathlib import Path

from PySide6.QtCore import Signal, QObject, Slot, QThread
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement

import logger
#import rig
import flrig

class LoggerWrapper(QObject):
    setStatus = Signal(str)
    clearStatus = Signal(str)
    logResponse = Signal(str)

    def __init__(self, logger, meta={}, parent=None):
        super().__init__(parent)
        self.logger = logger
        self.meta = {}

    @Slot(str, str, str, str, str, bool)
    def log(self, call, band, mode, exch, meta, force):
        self.meta.update(json.loads(meta))

        call = call.upper()
        qso_id = self.logger.log(call, band, mode, exch, json.dumps(self.meta),
                               force)
        self.logResponse.emit(qso_id)

    @Slot(str, str, str)
    def checkDupe(self, call, band, mode):
        call = call.upper()
        print(f"Checking dupe {call} {band} {mode}")
        if self.logger.dupe_check(call, band, mode):
            print("Duplicate!")
            self.setStatus.emit("duplicate")
        else:
            self.clearStatus.emit("duplicate")

class RigWrapper(QObject):
    updatedRigData = Signal(str, str, str)
    setStatus = Signal(str)
    clearStatus = Signal(str)
    triggerWorker = Signal()

    def __init__(self, rig, parent=None):
        super().__init__(parent)
        self.worker = RigWorker(rig)
        self.workerThread = QThread()
        self.worker.moveToThread(self.workerThread)
        self.worker.rigError.connect(self.setRigError)
        self.worker.updatedRigData.connect(self.dataFromWorker)
        self.triggerWorker.connect(self.worker.workerUpdate)
        self.workerThread.start()

    @Slot(str, str, str)
    def dataFromWorker(self, band, mode, freq):
        self.updatedRigData.emit(band, mode, freq)
        self.clearStatus.emit('rigerror')

    @Slot()
    def setRigError(self):
        self.setStatus.emit('rigerror')

    @Slot()
    def refreshRigData(self):
        self.triggerWorker.emit()

class RigWorker(QObject):
    updatedRigData = Signal(str, str, str)
    rigError = Signal()

    def __init__(self, rig, parent=None):
        super().__init__(parent)
        self.rig = rig

    @Slot()
    def workerUpdate(self):
        try:
            band = self.rig.get_band()
            mode = self.rig.get_mode()
            freq = str(self.rig.get_freq())
            self.updatedRigData.emit(band, mode, freq)
        except flrig.RigCommError as e:
            self.rigError.emit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('log', help='Name of database and log files',
                        default='qclog-defaultlog')
    parser.add_argument('-i', '--interface', default='fd')
    parser.add_argument('-o', '--operator')
    parser.add_argument('-b', '--band')
    parser.add_argument('-m', '--mode')
    parser.add_argument('-f', '--frequency')
    parser.add_argument('--flrig', help='Enable flrig', action='store_true')

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

    logger = LoggerWrapper(logger.Logger(args.log))
    context.setContextProperty("logger", logger)
    logger.setStatus.connect(root.setStatus)
    logger.clearStatus.connect(root.clearStatus)
    logger.logResponse.connect(root.logged)

    if args.flrig:
        rig = RigWrapper(flrig.Rig())
        context.setContextProperty("rig", rig)
        rig.updatedRigData.connect(root.populateRigData)
        rig.setStatus.connect(root.setStatus)
        rig.clearStatus.connect(root.clearStatus)
    else:
        root.populateRigData(args.band, args.mode, args.frequency)

    root.setup(args.operator)
    sys.exit(app.exec())
