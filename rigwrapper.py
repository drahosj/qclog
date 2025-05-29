from PySide6.QtCore import Signal, QObject, Slot, QThread, Property, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement

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
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.workerUpdate)
        self.timer.start(2000)

    @Slot()
    def workerUpdate(self):
        try:
            band = self.rig.get_band()
            mode = self.rig.get_mode()
            freq = str(self.rig.get_freq())
            self.updatedRigData.emit(band, mode, freq)
        except flrig.RigCommError as e:
            self.rigError.emit()
