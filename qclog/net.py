import json


from PySide6.QtCore import Signal, QObject, Slot, QTimer
from PySide6.QtNetwork import QUdpSocket, QHostAddress, QNetworkDatagram
from PySide6.QtNetwork import QAbstractSocket



class NetFunctions(QObject):

    def __init__(self, station_id, parent=None):
        super().__init__(parent)
        self.station_id = station_id

        self.socket = QUdpSocket(self)
        self.socket.bind(QHostAddress.LocalHost, 14300,
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

    def enable_heartbeat(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.send_heartbeat)
        self.timer.start(10000)

    def send_heartbeat(self):
        heartbeat = {
                "type" : "heartbeat",
                "sender" : self.station_id,
                "payload" : {
                    "station_id" : self.station_id
                    }
                }
        datagram = QNetworkDatagram()
        datagram.setData(json.dumps(heartbeat).encode())
        datagram.setDestination(QHostAddress.LocalHost, 14300)
        self.socket.writeDatagram(datagram)

