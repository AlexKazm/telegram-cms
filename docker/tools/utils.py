import time
import os


def exec(cmd: str):
    os.system(cmd)


def exec_iterable(iterable):
    step = 1
    for cmd in iterable:
        try:
            print("[{}]: Executing step {}".format(time.ctime(), step))
            step += 1
            exec(cmd)

        except:
            pass
