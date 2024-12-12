#! /usr/bin/env python3

# This Python file uses the following encoding: utf-8
import sys
import json

from pathlib import Path

from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

import logger
import rig

class LoggerWrapper(QObject):
    setStatus = Signal(str)

    def __init__(self, logger, meta=None, parent=None):
        super().__init__(parent)
        self.logger = logger
        self.meta = meta

    def log(self, call, band, mode, exch):
        call = call.upper()
        self.logger.log(call, band, mode, exch, json.dumps(meta))

    def check_dupe(self, call, band, mode):
        call = call.upper()
        print(f"Checking dupe {call} {band} {mode}")
        if self.logger.dupe_check(call, band, mode):
            print("Duplicate!")
            self.setStatus.emit("Duplicate entry!")

class RigWrapper(QObject):
    updateRigData = Signal(str, str, str)
    def __init__(self, rig, parent=None):
        super().__init__(parent)
        self.rig = rig

    def getRigData(self):
        band = self.rig.get_band()
        mode = self.rig.get_mode()
        freq = str(self.rig.get_freq())
        self.updateRigData.emit(band, mode, freq)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("./main.py <logname> <serialport> <rig_model> <operator>")
        exit(-1)

    sys.argv.pop(0)
    logname = sys.argv.pop(0)
    port = sys.argv.pop(0)
    model = int(sys.argv.pop(0))
    operator = sys.argv.pop(0).upper()
    meta = {"operator" : operator}

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    qml_file = Path(__file__).resolve().parent / "main.qml"
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)

    root = engine.rootObjects()[0]
    logger = LoggerWrapper(logger.Logger(logname), meta)
    root.doLog.connect(logger.log)
    root.checkDupe.connect(logger.check_dupe)
    logger.setStatus.connect(root.setStatus)

    rig = RigWrapper(rig.Rig(model, port))
    root.updateRigData.connect(rig.getRigData)
    rig.updateRigData.connect(root.populateRigData)

    root.setup(operator)
    sys.exit(app.exec())
