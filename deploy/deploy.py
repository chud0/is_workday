import logging
from pathlib import Path

import paramiko
from plumbum import local
from plumbum.machines.paramiko_machine import ParamikoMachine

BASE_DIR = Path(__file__).parent.parent

logging.basicConfig(format='%(levelname)-8s %(asctime)s  %(message)s', level=logging.INFO)
logger = logging.getLogger('deploy')


if __name__ == '__main__':
    host = local.env['DEPLOY_HOST']
    user = local.env['DEPLOY_USER']
    remote_dir = local.env['DEPLOY_DIR']
    deploy_key = local.env['DEPLOY_KEY']

    deploy_key_file = BASE_DIR / 'tmp'
    deploy_key_file.write_text('\n'.join(deploy_key.split('|')))

    try:
        with ParamikoMachine(
                host,
                user=user,
                keyfile=str(deploy_key_file),
                load_system_host_keys=False,
                missing_host_policy=paramiko.AutoAddPolicy(),
        ) as rem:
            rem.upload(BASE_DIR / 'deploy' / 'docker-compose.yml', f'{remote_dir}/docker-compose.yml')
            logger.info('Copy %s', 'docker-compose.yml')
            rem.upload(BASE_DIR / 'deploy' / 'nginx.conf', f'{remote_dir}/nginx.conf')
            logger.info('Copy %s', 'nginx.conf')

            docker_compose = rem['docker-compose']
            docker_compose['down', '--rmi', 'all']()
            logger.info('docker-compose stop')
            docker_compose['up', '-d']()
            logger.info('docker-compose up')
    finally:
        deploy_key_file.unlink()
