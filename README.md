# Overview 
Python scripts for working with [Seafile](https://www.seafile.com/en/home/) server.

# seafile_dl
This script can download file or folder in zip archive from Seafile library.
```
usage: seafile_dl.py [-h] [-o OUTPUT] -l LIBRARY -p PATH

Download file/folder from Seafile server

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Folder to save downloaded file
  -l LIBRARY, --library LIBRARY
                        Library name
  -p PATH, --path PATH  Path to folder or file inside Library (ex: buildXX/ )
```

# seafile_mon
Script for monitoring Seafile server.
It allows you two ping Seafile server via web_api and check user quota.
```
usage: seafile_mon.py [-h] [-c COMMAND] [-m EMAIL] [-u USER] [-p PASSWORD] -s
                      SERVER [-n] [-d]

optional arguments:
  -h, --help            show this help message and exit
  -c COMMAND, --command COMMAND
                        Command to execute (ping|quota)
  -m EMAIL, --email EMAIL
                        User each quote to check
  -u USER, --user USER  Auth User
  -p PASSWORD, --password PASSWORD
                        Auth User passwrod
  -s SERVER, --server SERVER
                        Seafile Server
  -n, --notify          Send notification if % is below 5
  -d, --debug           Debug mode
```