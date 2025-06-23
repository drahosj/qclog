import json
from datetime import datetime, timedelta
from collections import deque


from PySide6.QtCore import Signal, QObject, QTimer, Property, Slot, QTimer
from PySide6.QtNetwork import QUdpSocket, QHostAddress, QNetworkDatagram
from PySide6.QtNetwork import QAbstractSocket


class NetFunctions(QObject):
    remoteQsoReceived = Signal(dict)

    def __init__(self, qclog, parent=None):
        super().__init__(parent)
        self.qclog = qclog

        self.socket = QUdpSocket(self)
        self.socket.bind(QHostAddress.Any, 14300,
                         QAbstractSocket.ShareAddress |
                         QAbstractSocket.ReuseAddressHint)
        self.last_qso = {}
        self.heard_stations = {}
        self.last_resync = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.sendNextDatagram)
        self.timer.start(1000)
        self.queue = deque()

    def getLastQso(self):
        return self.last_qso

    def getHeardStations(self):
        return self.heard_stations

    lastQso = Property(dict, getLastQso)
    heardStations = Property(dict, getHeardStations)

    @Slot()
    def sendNextDatagram(self):
        if len(self.queue) > 0:
            self.socket.writeDatagram(self.queue.popleft())

    def start_listener(self):
        self.socket.readyRead.connect(self.read_datagram)

    def read_datagram(self):
        while self.socket.hasPendingDatagrams():
            datagram = self.socket.receiveDatagram()
            print(f"Sender: {datagram.senderAddress().toString()}")
            message = json.loads(datagram.data().data().decode())
            sender = message["sender"]
            if sender == self.qclog.station_id:
                print("\tSkipping own datagram")
                continue
            mtype = message["type"]
            if mtype == "qso":
                print(f"\tReceived remote qso from {sender}")
                qso = message["payload"]
                if sender in self.heard_stations:
                    qso['logged_by'] = self.heard_stations[sender]
                else:
                    qso['logged_by'] = sender
                self.last_qso = qso
                self.remoteQsoReceived.emit(qso)
            elif mtype == "heartbeat":
                hb_id = message["payload"]["station_id"]
                hb_name = message["payload"]["station_name"]
                print(f"\tHeartbeat: {hb_id} aka {hb_name}")
                self.handle_heartbeat(datagram.senderAddress(), message["payload"])
            elif mtype == "resync_request":
                print("\tReceived resync request")
                self.handle_resync_request(datagram.senderAddress(), message)
            elif mtype == "qso_list":
                self.handle_qso_list(datagram.senderAddress(), message)
            elif mtype == "qso_request":
                self.handle_qso_request(datagram.senderAddress(), message)
            else:
                print(f"\tUnknown message type `{mtype}`")

    def handle_heartbeat(self, address, hb):
        print(f"\t\t{hb}")
        hb_id = hb["station_id"]
        hb_name = hb["station_name"]
        self.heard_stations[hb_id] = hb_name
        hb_nqsos = hb["local_qso_count"]
        # TODO manage heard stations
        logged_nqsos = self.qclog.logger.getRemoteCount(hb_id)
        if hb_nqsos != logged_nqsos:
            print(f"\t\tQSO count mismatch - {logged_nqsos}/{hb_nqsos}")
            min_delta = timedelta(minutes=2)
            now = datetime.now()
            if self.last_resync is None or now - self.last_resync > min_delta:
                print("\t\t\tStarting a resync request")
                self.send_resync_request(address, hb_id)
                self.last_resync = now
            else:
                print("\t\t\tWaiting after last resync ({self.last_resync})")
        else:
            print("\t\tQSO counts agree, no resync needed")

    def send_qso(self, qso, dest=QHostAddress.Broadcast):
        message = {
                "type": "qso",
                "sender": self.qclog.station_id,
                "payload": qso
                }
        datagram = QNetworkDatagram()
        datagram.setData(json.dumps(message).encode())
        print(f"Sending qso broadcast for {message["payload"]["id"]}")
        datagram.setDestination(dest, 14300)
        self.queue.append(datagram)

    def enable_heartbeat(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.send_heartbeat)
        self.timer.start(10000)

    def send_heartbeat(self):
        heartbeat = {
                "type": "heartbeat",
                "sender": self.qclog.station_id,
                "payload": {
                    "station_id": self.qclog.station_id,
                    "station_name": self.qclog.station_name,
                    "local_qso_count": self.qclog.logger.getLocalCount()
                    }
                }
        datagram = QNetworkDatagram()
        datagram.setData(json.dumps(heartbeat).encode())
        datagram.setDestination(QHostAddress.Broadcast, 14300)
        self.queue.append(datagram)

    def send_resync_request(self, dest, target):
        print(f"\t\t\tSending resync request to {target}@{dest.toString()}")
        message = {
            "type": "resync_request",
            "sender": self.qclog.station_id,
            "target": target
            }
        datagram = QNetworkDatagram()
        datagram.setData(json.dumps(message).encode())
        #datagram.setDestination(dest, 14300)
        datagram.setDestination(QHostAddress.Broadcast, 14300)
        self.queue.append(datagram)
        print(f"\t\t\tResync request sent\n")

    def handle_resync_request(self, dest, message):
        if message["target"] != self.qclog.station_id:
            print("\t\tIt's not for us.")
            return
        sender = message["sender"]
        print(f"\t\tResync request from {sender}@{dest.toString()}")
        local_qsos = self.qclog.logger.getQsoList()
        chunks = [local_qsos[i:i + 10] for i in range(0, len(local_qsos), 10)]
        for chunk in chunks:
            message = {
                "type": "qso_list",
                "sender": self.qclog.station_id,
                "payload": chunk}
            datagram = QNetworkDatagram()
            datagram.setData(json.dumps(message).encode())
            #datagram.setDestination(dest, 14300)
            datagram.setDestination(QHostAddress.Broadcast, 14300)
            self.queue.append(datagram)
            print(f"\t\t\tQSO list chunk sent ({len(chunk)})")

    def handle_qso_list(self, dest, message):
        sender = message["sender"]
        print(f"\tQSO list received from {sender}")
        missing_list = []
        for qso in message["payload"]:
            if self.qclog.logger.logger.get_qso(qso) is None:
                print(f"\t\t{qso} - MISSING")
                missing_list.append(qso)
            else:
                print(f"\t\t{qso} - GOOD")
        print(f"Requesting {len(missing_list)} QSOs from {sender}")
        self.send_qso_request(dest, sender, missing_list)

    def send_qso_request(self, dest, target, qso_list):
        chunks = [qso_list[i:i + 10] for i in range(0, len(qso_list), 10)]
        for chunk in chunks:
            message = {
                "type": "qso_request",
                "sender": self.qclog.station_id,
                "target": target,
                "payload": chunk}
            datagram = QNetworkDatagram()
            datagram.setData(json.dumps(message).encode())
            #datagram.setDestination(dest, 14300)
            datagram.setDestination(QHostAddress.Broadcast, 14300)
            self.queue.append(datagram)
            print(f"\t\t\tQSO request chunk sent ({len(chunk)})")

    def handle_qso_request(self, dest, message):
        print("Handling QSO request")
        if message["target"] != self.qclog.station_id:
            print("\tIt isn't for us.")
            return

        for qso_id in message["payload"]:
            qso = self.qclog.logger.logger.get_qso(qso_id)
            sender = message["sender"]
            if qso is None:
                print(f"\tNonexistent QSO requested {qso_id}")
                return
            print(f"\tRe-sending {qso_id} to {sender}@{dest.toString()}")
            #self.send_qso(qso, dest)
            self.send_qso(qso)
