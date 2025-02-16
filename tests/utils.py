import logging
import os.path
import subprocess
from time import sleep

import docker

TESTNET_PATH = os.path.dirname(os.path.abspath(__file__))
client = docker.from_env()


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


def get_container_id(cnt: int = 1, return_all: bool = False) -> str | dict[str, list[dict[str, str | int]]] | None:
    containers_storage = {
        'bridge': [],
        'light': []
    }
    while cnt:
        containers = client.containers.list(all=True)
        for container in containers:
            if 'bridge' in container.name and not return_all:
                return container.short_id
            elif 'bridge' in container.name:
                containers_storage['bridge'].append({'auth_token': get_auth_token(container.short_id),
                                                     'port': int(container.ports['26658/tcp'][0]['HostPort'])})
            elif 'light' in container.name:
                containers_storage['light'].append({'auth_token': get_auth_token(container.short_id, 'light'),
                                                    'port': int(container.ports['26658/tcp'][0]['HostPort'])})
        if len(containers_storage['bridge']) + len(containers_storage['light']) >= 2:
            return containers_storage
        sleep(1)
        cnt -= 1


def get_auth_token(container_id: str, node_type: str | None = 'bridge') -> str:
    args = ['docker', 'exec', '-i', container_id,
            'celestia', node_type, 'auth', 'admin', '--p2p.network', 'private']
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
