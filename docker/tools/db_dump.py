from utils import exec_iterable

commands = [
    'mkdir dumps',
    'docker-compose up -d postgres',
    'docker exec -t telegramcms.postgres pg_dump -U telegramcms telegramcms_db --data-only > dumps/dump.pgsql',
    'docker-compose down'
]

if __name__ == '__main__':
    exec_iterable(commands)
