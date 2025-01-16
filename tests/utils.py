import logging
import os.path
import subprocess
from time import sleep

TESTNET_PATH = os.path.dirname(os.path.abspath(__file__))


def start_testnet() -> bool:
    args = ['docker', 'compose', '-f', f'{TESTNET_PATH}/testnet/docker-compose.yml', 'up', '-d']
    proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode == 0:
        return True
    logging.error(proc.stderr.decode('utf8'))
    return False


def stop_testnet() -> bool:
    args = ['docker', 'compose', '-f', f'{TESTNET_PATH}/testnet/docker-compose.yml', 'down']
    proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode == 0:
        return True
    logging.error(proc.stderr.decode('utf8'))
    return False


def get_container_id(cnt: int = 1) -> str | None:
    while cnt:
        proc = subprocess.run(['docker', 'ps'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        containers = dict((line.split()[1], line.split()[0])
                          for line in proc.stdout.decode('utf8').split('\n')[1:] if line)
        for name, id in sorted(containers.items(), key=lambda x: x[0], reverse=True):
            if name.startswith('bridge'):
                return id
        sleep(1)
        cnt -= 1
        if not cnt:
            if proc.returncode != 0:
                logging.error(proc.stderr.decode('utf8'))


def get_auth_token(container_id: str) -> str:
    args = ['docker', 'exec', '-i', container_id,
            'celestia', 'bridge', 'auth', 'admin', '--p2p.network', 'private']
    cnt = 10
    while cnt:
        proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode == 0:
            token = proc.stdout.decode('utf8').strip()
            return token
        sleep(1)
        cnt -= 1
        if not cnt:
            logging.error(proc.stderr.decode('utf8'))
