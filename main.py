#! /usr/bin/env python3

# This Python file uses the following encoding: utf-8
import sys
import json

from pathlib import Path

from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

import logger

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

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("./main.py <logname> <band> <mode> <operator>")
        exit(-1)

    sys.argv.pop(0)
    logname = sys.argv.pop(0)
    band = sys.argv.pop(0)
    mode = sys.argv.pop(0)
    operator = sys.argv.pop(0)
    meta = {"operator" : operator}

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    qml_file = Path(__file__).resolve().parent / "main.qml"
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)

    root = engine.rootObjects()[0]
    wrapper = LoggerWrapper(logger.Logger(logname), meta)
    root.doLog.connect(wrapper.log)
    root.checkDupe.connect(wrapper.check_dupe)
    wrapper.setStatus.connect(root.setStatus)
    root.setup(band, mode, operator)
    sys.exit(app.exec())
