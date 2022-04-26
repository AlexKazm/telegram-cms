FROM library/postgres:9.5
MAINTAINER @codefather-labs
COPY docker/config.yml /app/docker/config.yml
RUN apt-get update && apt-get install -y postgresql-client-common
WORKDIR /app/
USER root
COPY docker/postgres/init_db.sql /app/docker/init_db.sql
COPY docker/postgres/init_db.sql /docker-entrypoint-initdb.d/

COPY docker/wait-for-it.sh /app/docker/wait-for-it.sh
COPY docker/postgres/docker-entrypoint.sh /app/docker/docker-entrypoint.sh
COPY docker/postgres/init_db.sh /docker-entrypoint-initdb.d/init-user-db.sh

ENV POSTGRES_HOST_AUTH_METHOD=trust
ENV POSTGRES_USER=telegramcms
ENV POSTGRES_PASSWORD=telegramcms
ENV POSTGRESS_DB=telegramcms_db

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN chmod +x /app/docker/docker-entrypoint.sh
