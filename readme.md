## Quick start
`pip install -r requirements.txt`

`./main.py <logname> <band> <mode> <operator>`

Enter to log, escape to clear, tab to cycle fields

Dump log:

`./logger.py <logname>`

## Working features
- Logging
- Dupe checking
- Disaster recovery log (write-only)

## To Do
- Hamlib support to get band/mode/frequency (high priority)
- Dupe checking against remote logs
- Edit/Modify support in UI (meh priority)
