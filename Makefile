#gzip:
	#tar czf frontend.tar.gz frontend
	#tar czf telegram-cms.tar.gz *

push:
	git add .
	git commit -m "+autocommit"
	git push

clean:
	sudo rm -rf supervisor.log supervisor.pid

deploy:
	#make gzip
	make clean
	make push

wait:
	python3 -c "import time; time.sleep(3)"

docker_prune:
	sudo rm -rf migrations aerich.ini
	python3 docker/tools/prune.py

check_pgcli_installed:
	sh docker/tools/pgcli_installed.sh

db_cli:
	sudo make check_pgcli_installed
	docker-compose up -d postgres
	pgcli postgresql://telegramcms:telegramcms@0.0.0.0:5432/telegramcms_db
	# \q - выход

db_create:
	docker-compose up -d postgres
	make wait
	docker exec -it telegramcms.postgres psql -U telegramcms -f /app/docker/init_db.sql
	docker-compose down

db_drop:
	docker-compose up -d postgres
	docker exec -t telegramcms.postgres psql -U telegramcms -c "DROP DATABASE telegramcms_db;"
	docker-compose down

db_load:
	docker-compose up -d postgres
	make wait
	sudo psql -U telegramcms -h 0.0.0.0 -p 5432 -d telegramcms_db < dumps/dump.pgsql
	docker-compose down

db_load_base:
	docker-compose up -d postgres
	make wait
	sudo psql -U telegramcms -h 0.0.0.0 -p 5432 -d telegramcms_db < dumps/base.pgsql
	docker-compose down

db_migrate:
	docker-compose up -d
	make wait
	python3 docker/tools/migrate.py
	docker-compose down

db_rebuild:
	make db_drop
	make db_create
	make db_migrate

db_dump:
	python3 docker/tools/db_dump.py

build:
	docker-compose build --no-cache
	docker-compose up -d
	make db_create
	make db_migrate
	sudo apt-get install postgresql postgresql-contrib && make db_load
	docker-compose down

clear_images_buffer:
	docker-compose run services rm -rf services/telegram/plugins/image_generator/*.png