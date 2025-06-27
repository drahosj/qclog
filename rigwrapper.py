from PySide6.QtCore import Signal, QObject, Slot, QThread, Property, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement

from qclog.flrig import RigCommError


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

        self.watchdog = QTimer(self)
        self.watchdog.timeout.connect(self.setRigError)
        self.watchdog.start(4000)

    @Slot(str, str, str)
    def dataFromWorker(self, band, mode, freq):
        self.watchdog.start(4000)
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
        self.started = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.workerUpdate)
        self.timer.start(2000)

    def start(self):
        self.rig.start()

    @Slot()
    def workerUpdate(self):
        if not self.started:
            self.start()
            self.started = True

        try:
            freq = str(self.rig.get_freq())
            band = self.rig.get_band()
            mode = self.rig.get_mode()
            self.updatedRigData.emit(band, mode, freq)
        except RigCommError as e:
            self.rigError.emit()
