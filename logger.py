import sqlite3
import uuid
from datetime import datetime

class Logger:
    def __init__(self, logname):
        self.conn = sqlite3.connect(f"{logname}.db")
        cur = self.conn.cursor()
        cur.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' AND name='qsos';""")
        if cur.fetchone() is None:
            self.create_schema()
        cur.close()
        filename = f"{datetime.now().isoformat()}_{logname}.disaster_log"
        self.disaster_log = open(filename, "a")

    def close(self):
        self.conn.close()
        self.disaster_log.close()

    def create_schema(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE qsos (
                id TEXT,
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
                COALESCE(mod.exchange, qsos.exchange),
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
            CREATE VIEW log AS
            SELECT * FROM local_log;""")
        cur.close()

    def log(self, callsign, band, mode, exchange, meta=None, force=False):
        cur = self.conn.cursor()
        if (not force) and self.dupe_check(callsign, band, mode):
            return False
        qso_id = uuid.uuid4()
        entry = "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
            qso_id, datetime.now().isoformat(), callsign,
            band, mode, exchange, meta)
        self.disaster_log.write(entry)
        print(f"Logged: {entry}")

        data = [str(qso_id), callsign, band, mode, exchange, meta]
        cur.execute("""
            INSERT INTO qsos 
                (id, timestamp, callsign, band, mode, exchange, meta) 
            VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?);""", data)
        self.conn.commit()
        return True

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


if __name__ == "__main__":
    from sys import argv
    name = argv[1]
    logger = Logger(name)
    if argv[2] == "-l":
        logger.dump_log()
        exit()

    callsign = argv[2]
    band = argv[3]
    mode = argv[4]
    exch = argv[5]
    logger.log(callsign, band, mode, exch)
