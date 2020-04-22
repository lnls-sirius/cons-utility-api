#!/bin/bash
set -e
set -x
export FLASK_ENV=development
export FLASK_APP=$(pwd)/application

#export SPREADSHEET_SOCKET_PATH = current_app.config.get("SPREADSHEET_SOCKET_PATH")
export SPREADSHEET_XLSX_PATH='/home/carneirofc/Downloads/Redes e Beaglebones (1).xlsx'

flask run
