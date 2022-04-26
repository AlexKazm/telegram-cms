CREATE USER telegramcms WITH PASSWORD 'telegramcms';
CREATE DATABASE telegramcms_db WITH OWNER telegramcms;
GRANT ALL PRIVILEGES ON DATABASE telegramcms_db TO telegramcms;