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
