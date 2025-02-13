#! /usr/bin/env python3

# This Python file uses the following encoding: utf-8
import sys
import json

from pathlib import Path

from PySide6.QtCore import Signal, QObject, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement

import logger
#import rig
import flrig

class LoggerWrapper(QObject):
    setStatus = Signal(str)
    clearStatus = Signal(str)

    def __init__(self, logger, meta={}, parent=None):
        super().__init__(parent)
        self.logger = logger
        self.meta = {}

    @Slot(str, str, str, str, str)
    def log(self, call, band, mode, exch, meta):
        self.meta.update(json.loads(meta))

        call = call.upper()
        if not self.logger.log(call, band, mode, exch, json.dumps(self.meta)):
            self.setStatus.emit("duplicate")

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

    def __init__(self, rig, parent=None):
        super().__init__(parent)
        self.rig = rig

    @Slot()
    def refreshRigData(self):
        try:
            band = self.rig.get_band()
            mode = self.rig.get_mode()
            freq = str(self.rig.get_freq())
            self.updatedRigData.emit(band, mode, freq)
            self.clearStatus.emit("rigerror")
        except flrig.RigCommError as e:
            self.setStatus.emit("rigerror")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("./main.py <logname> <operator>")
        exit(-1)

    sys.argv.pop(0)
    logname = sys.argv.pop(0)

    operator = sys.argv.pop(0).upper()

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    qml_file = Path(__file__).resolve().parent / "main.qml"
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)

    root = engine.rootObjects()[0]
    context = engine.rootContext()

    logger = LoggerWrapper(logger.Logger(logname))
    context.setContextProperty("logger", logger)
    logger.setStatus.connect(root.setStatus)
    logger.clearStatus.connect(root.clearStatus)

    #rig = RigWrapper(rig.Rig(model, port))
    rig = RigWrapper(flrig.Rig())
    context.setContextProperty("rig", rig)
    rig.updatedRigData.connect(root.populateRigData)
    rig.setStatus.connect(root.setStatus)
    rig.clearStatus.connect(root.clearStatus)

    root.setup(operator)
    sys.exit(app.exec())
