FROM python:3.7-slim

ENV TZ=Europe/Moscow

COPY requirements.txt /tmp/

RUN pip3 install --requirement /tmp/requirements.txt

WORKDIR /home/app

RUN useradd -ms /bin/bash app_runner && chown -R app_runner:app_runner /home/app

COPY --chown=app_runner:app_runner . .

USER app_runner
