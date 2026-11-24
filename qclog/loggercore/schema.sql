CREATE TABLE qsos (
                id TEXT UNIQUE,
                station_id TEXT,
                timestamp DATETIME,
                band TEXT,
                mode TEXT,
                callsign TEXT,
                exchange JSON,
                meta JSON
            );
CREATE TABLE modifications (
                id TEXT UNIQUE,
                station_id TEXT,
                timestamp DATETIME,
                qso_id TEXT,
                qso_timestamp DATETIME,
                qso_callsign TEXT,
                qso_band TEXT,
                qso_mode TEXT,
                qso_exchange JSON,
                qso_meta JSON,
                FOREIGN KEY(qso_id) REFERENCES qsos(id)
            );
CREATE TABLE deletions (
                id TEXT UNIQUE,
                station_id TEXT,
                timestamp DATETIME,
                qso_id TEXT,
                FOREIGN KEY (qso_id) REFERENCES qsos(id)
            );
CREATE VIEW log AS
            SELECT
                id,
                qsos.station_id,
                COALESCE(mod.qso_timestamp, qsos.timestamp) timestamp,
                COALESCE(mod.qso_callsign, qsos.callsign) callsign,
                COALESCE(mod.qso_band, qsos.band) band,
                COALESCE(mod.qso_mode, qsos.mode) mode,
                COALESCE(mod.qso_exchange, qsos.exchange) exchange,
                COALESCE(mod.qso_meta, qsos.meta) meta,
                meta
            FROM qsos
            LEFT JOIN (
                SELECT qso_id, qso_callsign, qso_band, qso_mode, qso_exchange, qso_meta
                FROM modifications
                GROUP BY qso_id
                ORDER BY timestamp DESC
                LIMIT 1) mod
            ON mod.qso_id = id
            LEFT JOIN deletions
            ON deletions.qso_id = id
            WHERE deletions.qso_id IS NULL;
CREATE TABLE persistent_settings (
                key TEXT NOT NULL UNIQUE,
                value TEXT
            );
