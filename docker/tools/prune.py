from utils import exec_iterable

commands = [
    "sudo docker container stop $(docker ps -a -q)",
    "sudo docker container rm $(docker ps -a -q)",
    "sudo docker rmi -f $(docker images --filter dangling=true -q)",
    "sudo docker volume rm $(docker volume ls -f dangling=true -q)",
    "sudo docker system prune --all --force"
]

if __name__ == '__main__':
    exec_iterable(commands)
