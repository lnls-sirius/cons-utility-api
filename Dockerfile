FROM python:3.8

MAINTAINER Claudio Carneiro <claudio.carneiro@lnls.br>

USER root

WORKDIR /opt
RUN apt-get -y update && apt-get install -y apache2 apache2-dev

ADD ./requirements.txt /opt/requirements.txt
RUN pip install -r requirements.txt

ADD ./cons-common /opt/cons-common
RUN cd /opt/cons-common/ && pip install . && cd test/ && ./test_spreadsheet.py

ADD ./application /opt/application
ADD ./config.py /opt/config.py
ADD ./setup.py  /opt/setup.py
ADD ./start.sh  /opt/start.sh
ADD ./wsgi.py   /opt/wsgi.py
ADD ./entrypoint.sh   /opt/entrypoint.sh

RUN mkdir -p /opt/socket && chown -R www-data:www-data /opt/socket

ENV SPREADSHEET_SOCKET_PATH "/opt/socket/application.socket"
ENV SPREADSHEET_XLSX_PATH "/opt/spreadsheet/Redes e Beaglebones.xlsx"

CMD ["/opt/entrypoint.sh"]
