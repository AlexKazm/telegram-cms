FROM ubuntu:20.04

MAINTAINER @codefather-labs


# настройка таймзоны
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# обновляем репозитории и станавливаем зависимости к бубунте
RUN apt-get update
RUN apt-get -y install supervisor

# используем рута
USER root

RUN mkdir /app/
RUN chmod +rwx /app/

COPY frontend/ /app/frontend/

WORKDIR /app/frontend/

# установка ноды и npm
RUN apt-get install npm -y
#RUN npm i -g npm@3.10.10 -y
RUN apt-get install nodejs -y
#RUN npm run plugins
RUN npm install
RUN npm i -f

CMD npm run dev
#CMD /usr/bin/supervisord --configuration docker/frontend/supervisord.conf
