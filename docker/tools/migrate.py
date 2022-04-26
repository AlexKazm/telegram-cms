from utils import exec_iterable

commands = [
    "docker exec -it telegramcms.services aerich --app telegramcms init -t services.core.utils.database_config",
    "docker exec -it telegramcms.services aerich --app telegramcms init-db",
    "docker exec -it telegramcms.services aerich migrate --name drop_column",
    "docker exec -it telegramcms.services aerich upgrade",
]

if __name__ == '__main__':
    exec_iterable(commands)