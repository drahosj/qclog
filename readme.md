# Quick Contest Log (QCLog)

## Installation
The only dependency is PySide6. If you have a systemwide PySide6 installation,
it might work without any dependencies. Just clone the repo.

`git clone https://github.com/drahosj/quicklog`

Otherwise, you might need to install PySide6 in a virtualenv as follows:

`cd quicklog`

`python3 -m venv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

It should be good to go.

## Running
From the QCLog directory

`source venv/bin/activate` (if not already active)

`./main.py <name-of-log-file>`

The only mandatory argument is a name to use for the log files and DB.
`./main.py --help` for more info.

It's highly recommended to run with flrig enabled (--flrig) to automatically
populate band/mode/frequency from the radio.

## General Usage
Enter to log, escape to clear, tab to cycle fields.

QCLog will warn on a duplicate entry (band/mode/call) and refuse to log
incomplete entries or dupes unless you force-log (ctrl-escape).

Right click any of the output fields (band/mode/frequency/operator) to change.

## Log storage
Logs are stored in a sqlite database with a relatively simple schema. Logs are
also dumped to plain append-only log opened on startup for disaster recovery.

Default directory for storing logs is `~/.qclog`. `-d`/`--data-dir` can change this.

## Log export
The log DB engine (plain Python; no QT dependencies) supports some
useful functionality on its own. You can dump logs from the log directory 
(default `~/.qclog`):

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
