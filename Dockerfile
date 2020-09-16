FROM python:3.8.5-slim-buster

MAINTAINER Claudio Carneiro <claudio.carneiro@lnls.br>

USER root

WORKDIR /opt

RUN apt-get -y update && apt-get install --no-install-recommends -y\
    apache2 apache2-dev && rm -rf /var/lib/apt/lists/*

ADD . /opt

RUN mkdir -p /opt/socket && chown -R www-data:www-data /opt/socket &&\
    pip install -r requirements.txt && apt remove -y apache2-dev

ENV SPREADSHEET_SOCKET_PATH "/opt/socket/application.socket"
ENV SPREADSHEET_XLSX_PATH "/opt/spreadsheet/Redes e Beaglebones.xlsx"

CMD ["/opt/entrypoint.sh"]
