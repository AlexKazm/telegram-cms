# Loadtesting dockerfile image
FROM ubuntu:18.04

MAINTAINER @codefather-labs

RUN apt-get update
RUN apt-get install -y gcc g++ cmake python3.8 python3-dev python3-pip supervisor

RUN apt-get -y install gcc g++ cmake libc-dev python3.8 python3-dev python3-pip nano \
            libpq-dev build-essential libffi-dev \
            libssl-dev openssl wget \
            coreutils dpkg-dev dpkg \
            apt-transport-https lsb-release ca-certificates \
            curl supervisor

COPY docker/locust/requirements.txt /app/requirements.txt
COPY tests/loadtests/ /app/

WORKDIR /app/
USER root

RUN chmod -R +rwx /app
RUN chmod -R +rwx $(which python3)
RUN python3.8 -m pip install -r /app/requirements.txt

CMD /usr/bin/supervisord --configuration docker/locust/supervisord.conf