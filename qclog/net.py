import json


from PySide6.QtCore import Signal, QObject, QTimer, Property
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
        self.last_qso = None

    def getLastQso(self):
        return self.last_qso

    def setLastQso(self, uuid):
        self.last_qso = uuid

    lastQso = Property(dict, getLastQso, setLastQso)

    def start_listener(self):
        self.socket.readyRead.connect(self.read_datagram)

    def read_datagram(self):
        while self.socket.hasPendingDatagrams():
            datagram = self.socket.receiveDatagram()
            print(f"Sender: {datagram.senderAddress().toString()}")
            message = json.loads(datagram.data().data().decode())
            sender = message["sender"]
            if sender == self.station_id:
                print("\tSkipping own datagram")
                continue
            mtype = message["type"]
            if mtype == "qso":
                print(f"\tReceived remote qso from {sender}")
                qso = message["payload"]
                self.remoteQsoReceived.emit(qso)
                self.setLastQso(qso)
            elif mtype == "heartbeat":
                hb_id = message["payload"]["station_id"]
                hb_name = message["payload"]["station_name"]
                print(f"\tHeartbeat: {hb_id} aka {hb_name}")
            else:
                print(f"\tUnknown message type `{mtype}`")

    def send_qso(self, qso):
        message = {
                "type": "qso",
                "sender": self.station_id,
                "payload": qso
                }
        datagram = QNetworkDatagram()
        datagram.setData(json.dumps(message).encode())
        print(f"Sending qso broadcast for {message["payload"]["id"]}")
        datagram.setDestination(QHostAddress.Broadcast, 14300)
        self.socket.writeDatagram(datagram)

    def enable_heartbeat(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.send_heartbeat)
        self.timer.start(10000)

    def send_heartbeat(self):
        heartbeat = {
                "type": "heartbeat",
                "sender": self.station_id,
                "payload": {
                    "station_id": self.station_id,
                    "station_name": self.station_name
                    }
                }
        datagram = QNetworkDatagram()
        datagram.setData(json.dumps(heartbeat).encode())
        datagram.setDestination(QHostAddress.Broadcast, 14300)
        self.socket.writeDatagram(datagram)

