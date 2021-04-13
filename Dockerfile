FROM python:3.8-alpine

RUN adduser -D diagnosticator

RUN apk add --no-cache bash mariadb-dev mariadb-client python3-dev build-base libffi-dev openssl-dev

WORKDIR /home/diagnosticator

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn pymysql

COPY app app
COPY .flaskenv .flaskenv
COPY main.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP main.py

RUN chown -R diagnosticator:diagnosticator ./
USER diagnosticator

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
