#!/bin/bash
set -e
set -x

#export SPREADSHEET_SOCKET_PATH='/var/tmp/socket'
export SPREADSHEET_XLSX_PATH='/home/carneirofc/Downloads/Redes e Beaglebones (1).xlsx'

flask run
