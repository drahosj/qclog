from PySide6.QtCore import Signal, QObject, Slot, QThread, Property, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement

class FldigiWorker(QObject):
    fldigiLogCallChanged = Signal(str)

    def __init__(self, fldigi, parent=None):
        super().__init__(parent)
        self.fldigi = fldigi
        self.log_call = ''

    @Slot()
    def updateFldigiLogCall(self):
        old_call = self.log_call
        self.log_call = self.fldigi.get_call()
        if old_call != self.log_call:
            print("fldigi log call changed to " + self.log_call)
            self.fldigiLogCallChanged.emit(self.log_call)

    def getLogCall(self):
        return self.log_call
    
    def setLogCall(self, call):
        self.log_call = call

    lastCall = Property(str, getLogCall, setLogCall)

class FldigiWrapper(QObject):
    logCallChanged = Signal(str)

    def __init__(self, fldigi, parent=None):
        super().__init__(parent)
        self.worker = FldigiWorker(fldigi)
        self.workerThread = QThread()
        self.worker.moveToThread(self.workerThread)
        self.worker.fldigiLogCallChanged.connect(self.logCallChanged)
        self.workerThread.start()
        timer = QTimer(self)
        timer.timeout.connect(self.worker.updateFldigiLogCall)
        timer.start(100)
