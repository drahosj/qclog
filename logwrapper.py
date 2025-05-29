from PySide6.QtCore import Signal, QObject, Slot, QThread, Property, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement

class LoggerWrapper(QObject):
    setStatus = Signal(str)
    clearStatus = Signal(str)
    populateEntry = Signal(str, str)
    logResponse = Signal(str)
    qsoLogged = Signal(str)
    last_qso = None

    def __init__(self, logger, meta={}, parent=None):
        super().__init__(parent)
        self.logger = logger
        self.meta = meta

    @Slot(str, str, str, str, str, bool)
    def log(self, call, band, mode, exch, meta, force):
        self.meta.update(json.loads(meta))

        call = call.upper()
        qso_id = self.logger.log(call, band, mode, exch, json.dumps(self.meta),
                               force)
        self.logResponse.emit(qso_id)
        if qso_id is not None:
            last_qso = qso_id
            self.qsoLogged.emit(self.logger.get_json_qso(qso_id))

    @Slot(str)
    def log_remote(self, json_qso):
        self.logger.add_remote_qso(json.loads(json_qso))

    @Slot(str, str, str)
    def checkDupe(self, call, band, mode):
        call = call.upper()
        print(f"Checking dupe {call} {band} {mode}")
        if self.logger.dupe_check(call, band, mode):
            print("Duplicate!")
            self.setStatus.emit("duplicate")
        else:
            self.clearStatus.emit("duplicate")

    @Slot()
    def undoLast(self):
        call, exch = self.logger.undo_last()
        print(f"Last undone #{call} (#{exch})")
        self.populateEntry.emit(call, exch)
        
    def getLastQso(self):
        return self.last_qso

    def setLastQso(self, uuid):
        self.last_qso = uuid

    lastQso = Property(str, getLastQso, setLastQso)
