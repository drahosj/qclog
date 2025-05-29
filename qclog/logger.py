#! /usr/bin/env python3

import sqlite3
import uuid
import json
from datetime import datetime
from pathlib import Path

class Logger:
    def __init__(self, logname, datadir=Path('.')):
        self.conn = sqlite3.connect(datadir / f"{logname}.db")
        cur = self.conn.cursor()
        cur.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' AND name='qsos';""")
        if cur.fetchone() is None:
            self.create_schema()
        cur.close()
        filename = f"{datetime.now().isoformat()}_{logname}.disaster_log"
        self.disaster_log = open(datadir / filename, "a")

    def close(self):
        self.conn.close()
        self.disaster_log.close()

    def create_schema(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE qsos (
                id TEXT UNIQUE,
                timestamp DATETIME,
                band TEXT,
                mode TEXT,
                callsign TEXT,
                exchange JSON,
                meta JSON
            );""")
        cur.execute("""
            CREATE TABLE modifications (
                qso_id TEXT,
                timestamp DATETIME,
                callsign TEXT,
                band TEXT,
                mode TEXT,
                exchange JSON,
                FOREIGN KEY(qso_id) REFERENCES qsos(id)
            );""")
        cur.execute("""
            CREATE TABLE deletions (
                qso_id TEXT,
                timestamp DATETIME,
                FOREIGN KEY (qso_id) REFERENCES qsos(id)
            );""")
        cur.execute("""
            CREATE VIEW local_log AS
            SELECT
                id,
                qsos.timestamp timestamp,
                COALESCE(mod.callsign, qsos.callsign) callsign,
                COALESCE(mod.band, qsos.band) band,
                COALESCE(mod.mode, qsos.mode) mode,
                COALESCE(mod.exchange, qsos.exchange) exchange,
                meta
            FROM qsos
            LEFT JOIN (
                SELECT qso_id, callsign, band, mode, exchange
                FROM modifications
                GROUP BY qso_id
                ORDER BY timestamp DESC
                LIMIT 1) mod
            ON mod.qso_id = id
            LEFT JOIN deletions
            ON deletions.qso_id = id
            WHERE deletions.qso_id IS NULL;""");
        cur.execute("""
            CREATE TABLE remote_qsos (
                id TEXT UNIQUE,
                timestamp DATETIME,
                band TEXT,
                mode TEXT,
                callsign TEXT,
                exchange JSON,
                meta JSON
                );""")
        cur.execute("""
            CREATE VIEW log AS
                SELECT * FROM local_log
            UNION
                SELECT * FROM remote_qsos
            ;""")
        cur.execute("""
            CREATE TABLE persistent_settings (
                key TEXT NOT NULL UNIQUE,
                value TEXT
            );""")
        cur.close()

    def add_remote_qso(self, qso):
        cur = self.conn.cursor()
        data = [
                qso["id"],
                qso["timestamp"],
                qso["callsign"],
                qso["band"],
                qso["mode"],
                qso["exchange"],
                qso["meta"]]
        cur.execute("""
            INSERT INTO remote_qsos 
                (id, timestamp, callsign, band, mode, exchange, meta) 
            VALUES (?, ?, ?, ?, ?, ?, ?);""", data)
        self.conn.commit()

    def get_json_qso(self, qso_id):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT
                id, timestamp, callsign, band, mode, exchange, meta
            FROM
                log
            WHERE
                id = ?;""", [qso_id])
        qso = cur.fetchone()
        cur.close()
        return json.dumps({
            "id" : qso[0],
            "timestamp" : qso[1],
            "callsign" : qso[2],
            "band" : qso[3],
            "mode" : qso[4],
            "exchange" : json.loads(qso[5]),
            "meta" : json.loads(qso[6])})


    def log(self, callsign, band, mode, exchange, meta=None, force=False):
        cur = self.conn.cursor()
        if (not force) and self.dupe_check(callsign, band, mode):
            return None
        qso_id = uuid.uuid4()
        entry = "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
            qso_id, datetime.now().isoformat(), callsign,
            band, mode, exchange, meta)
        self.disaster_log.write(entry)
        self.disaster_log.flush()
        print(f"Logged: {entry}")

        data = [str(qso_id), callsign, band, mode, exchange, meta]
        cur.execute("""
            INSERT INTO qsos 
                (id, timestamp, callsign, band, mode, exchange, meta) 
            VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?);""", data)
        self.conn.commit()
        return str(qso_id)

    def dupe_check(self, callsign, band, mode):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id
            FROM log
            WHERE callsign=?
            AND band=?
            AND mode=?;""", [callsign, band, mode]);
        return not (cur.fetchone() is None)

    def dump_log(self):
        cur = self.conn.cursor()
        print("Timestamp\tBand\tMode\tCallsign\tExch")
        for row in cur.execute("SELECT * FROM log;"):
            print(f"{row[1]}\t{row[3]}\t{row[4]}\t{row[2]}\t{row[5]}")

    def set_setting(self, key, value):
        print(f"Saving persistent setting {key}={value}")
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO 
                persistent_settings (key, value)
            VALUES 
                (?, ?)
            ON CONFLICT(key) DO
            UPDATE SET value=?;""", [key, value, value])
        self.conn.commit()
        cur.close()

    def get_setting(self, key):
        cur = self.conn.cursor()
        for row in cur.execute("""
            SELECT value FROM persistent_settings
            WHERE key=?;""", [key]):
            return row[0]
        return None


    def undo_last(self):
        cur = self.conn.cursor()
        for row in cur.execute("""
                SELECT
                    id, callsign, exch
                FROM qsos 
                ORDER BY timestamp DESC 
                LIMIT 1;"""):
            print(f"Deleting QSO {row[1]}")
            cur = self.conn.cursor()
            cur.execute("INSERT INTO deletions VALUES (?, ?);",
                        [row[0], datetime.now().isoformat()])
            return row[1], row[2]
        return "", ""


    def cabrillo(self, exchfmt):
        cur = self.conn.cursor()
        qsos = []
        for row in cur.execute("SELECT * FROM log;"):
            dt = datetime.fromisoformat(row[1])
            date = dt.date().isoformat()
            time = dt.time().strftime("%H%M")
            freq = cabrillo_band_map[row[3]].rjust(5)
            mode = cabrillo_mode_map[row[4]]
            call = row[2]
            exch = json.loads(row[5])
            meta = json.loads(row[6])
            exch = format_exchange(exchfmt, call, exch, meta)
            s = f"QSO: {freq} {mode} {date} {time} {exch}"
            qsos.append(s)
        return "\n".join(qsos)

cabrillo_band_map = {
        "160M" : "1800",
        "80M" : "3500",
        "40M" : "7000",
        "20M" : "14000",
        "15M" : "21000",
        "10M" : "28000",
        "6M" : "50",
        "2M" : "144",
        }

cabrillo_mode_map = {
        "LSB" : "PH",
        "USB" : "PH",
        "SSB" : "PH",
        "AM" : "PH",
        "CW-U" : "CW",
        "CW-L" : "CW",
        "DIG-U" : "DG",
        "DIG-L" : "DG",
        "DATA-U" : "DG",
        "DATA-L" : "DG",
        "DATA" : "DG",
        "FM" : "FM",
        "RTTY" : "RY"
        }


def format_exchange(fmt, call, exch, meta):
    res = []
    for token in fmt.split():
        if token[0:2] == '%E':
            key, width = token[2:].split(':')
            s = exch[key].upper()
            res.append(s.ljust(int(width)))
        elif token[0:2] == '%M':
            key, width = token[2:].split(':')
            s = meta[key].upper()
            res.append(s.ljust(int(width)))
        elif token[0:2] == '%C':
            width = token.split(':')[-1]
            s = call
            res.append(s.ljust(int(width)))
        else:
            s, width = token.split(':')
            res.append(s.ljust(int(width)))
    return " ".join(res)


if __name__ == "__main__":
    from sys import argv
    if argv[1] == "-l":
        name = argv[2]
        logger = Logger(name)
        logger.dump_log()
        exit()

    if argv[1] == "-c":
        fmt = argv[2]
        name = argv[3]
        logger = Logger(name)
        print(logger.cabrillo(fmt))
        exit()

    if argv[1] == "-g":
        name = argv[2]
        qso_id = argv[3]
        logger = Logger(name)
        print(logger.get_json_qso(qso_id))
        exit()

    name = argv[1]
    logger = Logger(name)

    callsign = argv[2]
    band = argv[3]
    mode = argv[4]
    exch = argv[5]
    logger.log(callsign, band, mode, exch)
