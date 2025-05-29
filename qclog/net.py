import json


from PySide6.QtCore import Signal, QObject, Slot, QTimer
from PySide6.QtNetwork import QUdpSocket, QHostAddress, QNetworkDatagram
from PySide6.QtNetwork import QAbstractSocket



class NetFunctions(QObject):
    remoteQsoReceived = Signal(dict)

    def __init__(self, gv, parent=None):
        super().__init__(parent)
        self.station_id = gv.station_id
        self.station_name = gv.station_name

        self.socket = QUdpSocket(self)
        self.socket.bind(QHostAddress.Any, 14300,
                         QAbstractSocket.ShareAddress | 
                         QAbstractSocket.ReuseAddressHint)

    def start_listener(self):
        self.socket.readyRead.connect(self.read_datagram)

    def read_datagram(self):
        while self.socket.hasPendingDatagrams():
            datagram = self.socket.receiveDatagram()
            print("Received datagram")
            print(f"Sender: {datagram.senderAddress()}")
            print(f"Data: {datagram.data()}")
            message = json.loads(datagram.data().data().decode())
            if message["type"] == "qso":
                qso = message["payload"]
                self.remoteQsoReceived.emit(json.dumps(qso))


    def send_qso(self, qso):
        message = {
                "type" : "qso",
                "sender" : self.station_id,
                "payload" : json.loads(qso)
                }
        datagram = QNetworkDatagram()
        datagram.setData(json.dumps(message).encode())
        datagram.setDestination(QHostAddress.Broadcast, 14300)
        self.socket.writeDatagram(datagram)

    def enable_heartbeat(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.send_heartbeat)
        self.timer.start(10000)

    def send_heartbeat(self):
        heartbeat = {
                "type" : "heartbeat",
                "sender" : self.station_id,
                "payload" : {
                    "station_id" : self.station_id,
                    "station_name" : self.station_name
                    }
                }
        datagram = QNetworkDatagram()
        datagram.setData(json.dumps(heartbeat).encode())
        datagram.setDestination(QHostAddress.Broadcast, 14300)
        self.socket.writeDatagram(datagram)

