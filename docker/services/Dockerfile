FROM ubuntu:18.04

MAINTAINER @codefather-labs

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update
RUN apt-get install -y gcc g++ cmake python3.8 python3-dev python3-pip supervisor

RUN apt-get -y install gcc g++ cmake libc-dev python3.8 python3.8-dev python3-dev python3-pip nano \
            libpq-dev build-essential libffi-dev \
            libssl-dev openssl wget \
            coreutils dpkg-dev dpkg \
            apt-transport-https lsb-release ca-certificates \
            curl supervisor git


WORKDIR /app/
USER root

RUN chmod -R +rwx /app
RUN chmod -R +rwx $(which python3)

COPY services /app/services/
COPY frontend /app/frontend/
COPY requirements.txt /app/requirements.txt

RUN chmod -R +rwx /app
RUN chmod -R +rwx $(which python3)
RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install -r /app/requirements.txt
RUN python3.8 -m pip install -U https://github.com/pyrogram/pyrogram/archive/asyncio.zip
RUN python3.8 -m pip install -U tortoise-orm
RUN python3.8 -m pip install fastapi_contrib[all] pytz aiocache[redis]
RUN python3.8 -m pip install aerich==0.2.2
RUN aerich --version

#ENTRYPOINT ["docker/services/wait_for_kafka.sh"]
EXPOSE 9000 8084

CMD /usr/bin/supervisord --configuration docker/services/supervisord.conf