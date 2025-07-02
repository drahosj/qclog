# Quick Contest Log (QCLog) (next section)

## Installation
The only dependency is PySide6 (hamlib - sad and **BROKEN** so don't worry about it). 
If you have a systemwide PySide6 installation,
it might work without any dependencies. Just clone the repo.

`git clone https://github.com/drahosj/quicklog`

### Installing Dependencies System-Wide

Fedora: `# dnf install python3-pyside6`

**NOTE**: deb-based distros don't seem to package pyside6 system-wide,
so a virtualenv is recommended (next section)

### Installing dependencies in a virtualenv

`cd quicklog`

`python3 -m venv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

Remember to activate the venv before trying to run qclog.

NOTE: Hamlib doesn't play nice with pip, hamlib probably won't work
in a venv no matter what.

### Flatpak
**BETA** - Stuff might not work (networking?)

Not published on flathub (yet). Build it locally:

`flatpak-builder --force-clean --user --install-deps-from=flathub --repo=repo --install builddir me.drahos.QCLog.yml`

Run like a normal flatpak:

`flatpak run me.drahos.QCLog <args>`

Data ends up in `$HOME/.var/app/me.drahos.QCLog/data` (you can point --data-dir
at this to do log exports etc. from the non-flatpak version)

## Running
From the QCLog directory

`./main.py <name-of-log-file>`

The only mandatory argument is a name to use for the log files and DB.
`./main.py --help` for more info.

Provide a station name on first startup (station name is persisted in
the DB for subsequent runs with the same log file) for better notifications
when other stations log contacts.

It's highly recommended to run with flrig enabled (--flrig) to automatically
populate band/mode/frequency from the radio.

## General Usage
NOTE: QCLog is really intended to run in a tiling window manager combined with
whatever else you'd like. It's minimalist for a reason. With a floating
window manager, just try to resize it to where you want and use
your preferred key combination to bring it in focus as needed.

Enter to log, escape to clear, tab to cycle fields.

QCLog will warn on a duplicate entry (band/mode/call) and refuse to log
incomplete entries or dupes unless you force-log (ctrl-enter).

Force-log will log an incomplete/invalid/duplicate/wildly incorrect entry. This
can be used to take notes (editing previous entries is not possible, nor is
undoing/deleting - just leave yourself something easy to grep for and
clean it up later in the cabrillo)

Right click any of the output fields (band/mode/frequency/operator) to change.

### Recommended Run Commands
These will assume that "fd" is the name of the log you want to use (field day).
Field day is the default logging interface. Other interfaces exist and
can be chosen with `-i` (eg. POTA).



### Running with FLDIGI for a digital station
Situation: FLDigi for digital modes station. Rig access needs to be shared
between quicklog and fldigi.

1. Start flrig and configure appropriately
2. Start fldigi
3. `./main.py fd -n 'Digital Modes Station' --flrig --fldigi`

fldigi will be able to key the rig and populate frequency/mode/etc.
QClog will populate band/mode/frequency from flrig (--flrig). When
you click on a callsign in fldigi, it will populate automatically in
qclog and give you immediate dupe checking (--fldigi).

### Phone/CW station
NOTE: hamlib is definitely broken right now, doesn't work.

Example situation: FT-450D connected via a DigiRig on /dev/ttyACM0.
38400 baud, handshake has to be turned off in hamlib because RTS
would otherwise key the rig constantly.

`./main.py fd -n 'Phone Station' --hamlib
1046,/dev/ttyUSB0,38400,serial_handshake=None,parity=None`

## Log storage
Logs are stored in a sqlite database with a relatively simple schema. Logs are
also dumped to plain append-only log opened on startup for disaster recovery.

Default directory for storing logs is `$XDG_DATA_HOME/qclog`. `-d`/`--data-dir` can change this.

## Network
Simple UDP IPv4 broadcast on port 14300. Syncs logs for dupe checking purposes.
Title bar updates when another station logs an entry

## Log export
The log DB engine (plain Python; no QT dependencies) supports some
useful functionality on its own. You can dump logs from the log directory 
(default `$XDG_DATA_HOME/qclog`):

`/path/to/logger.py -l <logname>`

The logname should be the same as specified when running the log application.

### Cabrillo export
Rudimentary Cabrillo export is supported.

`./logger.py -c <template string> <logname>`

The template string is a whitespace-separated list of tokens. Each
token consists of a literal or template. The supported templates are:

- %C (callsign)
- %E\<key\> Key taken from exchange field
- %M\<key\> Key taken from metadata field

The frequency is currently extracted from the 'band', even if exact frequency is
available in the metadata

For example, 
`./logger.py -c 'N0CALL:13 2A:2 IA:2 %C:13 %Eclass:2 %Esection:2' fd`

will export a field-day style Cabrillo log, consisting of standard QSO lines
with frequency, mode, date, time, and then (as specified by the template string)
mycall, myclass, mysection (in the template string, these are constants) and
then the call, class, and section taken from the QSO. The logs will be exported
from fd.db

## License ##
BSD 2-Clause
