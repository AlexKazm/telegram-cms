import time
import argparse
import subprocess

from yaml import load as yaml_load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def is_iterable(obj):
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True


def exec(cmd: str):
    subprocess.call(cmd, shell=True)
    time.sleep(1)


def exec_iterable(iterable):
    step = 1
    for cmd in iterable:
        try:
            print("[{}]: Executing step {}".format(time.ctime(), step))
            exec(iterable['step{}'.format(step)])
            step += 1
        except:
            pass


def try_parse_or_none(from_fict: dict, param: str):
    try:
        return from_fict[param]
    except KeyError:
        return None


def assert_is_not_none(subject: str):
    assert subject is not None


def make_for_iter(iter, subject):
    for i in iter:
        subject(i)


def gen_dockerfile(container, data):
    print(data)
    path = "docker/{}".format(data['dockerfile'])
    _from = try_parse_or_none(data, 'from')
    maintainer = try_parse_or_none(data, 'maintainer')
    command = try_parse_or_none(data, 'startup')

    lines = [
        f"FROM {_from}\n",
        f"MAINTAINER {maintainer}\n"
        f"COPY docker/config.yml /app/docker/config.yml\n"
        f"WORKDIR /app/\n"
        f"USER root\n"
    ]

    if container == 'postgres':
        lines.append(
            f"COPY docker/postgres/init_db.sql /app/docker/init_db.sql\n"
            f"COPY docker/postgres/init_db.sql /docker-entrypoint-initdb.d/\n"
        )

    if container == 'services':
        lines.append(
            f"COPY services /app/services/\n"
            f"COPY static /app/static/\n"
            f"COPY templates /app/templates/\n"
            f"COPY requirements.txt /app/requirements.txt\n"
            f"RUN chmod -R +rwx /app\n"
            f"RUN chmod -R +rwx $(which python3)\n"
            f"RUN python3 -m pip install --upgrade pip\n"
            f"RUN python3 -m pip install -r /app/requirements.txt\n"
        )
    with open(path, 'w', encoding='utf-8') as dockerfile:
        dockerfile.writelines(lines)


def parse_config_data(data: dict):
    result = {}
    result.update({"version": "3", "services": {}})
    for container in data:
        point = data[container]

        dockerfile: str = try_parse_or_none(point, 'dockerfile')
        connection: dict = try_parse_or_none(point, 'connection')
        restart: str = try_parse_or_none(point, 'restart')
        depends_on: list = try_parse_or_none(point, 'with')
        command: str = try_parse_or_none(point, 'startup')
        environment: dict = try_parse_or_none(point, 'environment')

        _from: str = try_parse_or_none(point, 'from')
        _maintainer: str = try_parse_or_none(point, 'maintainer')

        database: str = try_parse_or_none(connection, 'DATABASE')
        user: str = try_parse_or_none(connection, 'USER')
        password: str = try_parse_or_none(connection, 'PASSWORD')
        host: int = try_parse_or_none(connection, 'HOST')
        port: int = try_parse_or_none(connection, 'PORT')

        gen_dockerfile(container, point)

        result['services'].update({
            f"{container}": {
                "container_name": f"docker.{container}",
                "restart": restart,
                "depends_on": depends_on,
                "build": {
                    "context": ".",
                    "dockerfile": f"docker/{dockerfile}",
                }
            }
        })

        if environment:
            result['services'][container]['environment'] = environment

        if command:
            result['services'][container]['command'] = str(command)

    stream = open('docker-compose.yml', 'w', encoding='utf-8')
    composer = dump(result, stream=stream)


def compose_generator(buildfile: str):
    required = ['version', 'staging', 'production']
    try:
        f = open(buildfile, 'r', encoding='utf-8')
        yml = yaml_load(f.read(), Loader=Loader)
        f.close()
    except:
        return print("Cant find config file")

    subjects = []

    for req in required:
        subjects.append(try_parse_or_none(yml, req))

    make_for_iter(subjects, assert_is_not_none)
    parse_config_data(yml[try_parse_or_none(yml, 'version')])


def parse_target(target: str, build_file: str):
    f = open(build_file, 'r', encoding='utf-8')

    try:
        yml = yaml_load(f.read(), Loader=Loader)[target]
    except KeyError:
        print("Cant find target {}".format(target))
        return

    f.close()

    if type(yml) == dict:
        return exec_iterable(yml)

    elif type(yml) == str:
        exec(yml)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', help='Getting available targets in build.yml file')
    parser.add_argument('--build_file', help='Getting available targets in build.yml file')
    parser.add_argument('--generate_composer', help='Generating docker-compose file from config.yml')

    args = parser.parse_args()
    if args.target and args.build_file:
        try:
            parse_target(args.target, args.build_file)
        except KeyboardInterrupt:
            exit(0)

    elif args.generate_composer:
        try:
            compose_generator(args.generate_composer)
        except KeyboardInterrupt:
            exit(0)

    else:
        raise IndexError("Target is required. Getting available targets in build.yml file")
