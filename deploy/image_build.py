import json
import logging
from pathlib import Path
from plumbum import local
import yaml

logging.basicConfig(format='%(levelname)-8s %(asctime)s  %(message)s', level=logging.INFO)
logger = logging.getLogger('deploy')

BASE_DIR = Path(__file__).parent.parent

docker = local['docker']


def build_docs(template_path: Path, yaml_path: Path, doc_path: Path) -> None:
    template = template_path.read_text()
    spec = yaml.load(yaml_path.read_text(), Loader=yaml.FullLoader)
    doc_path.write_text(template % json.dumps(spec, default=str))

    logger.info('Doc file saved to: %s', doc_path)


if __name__ == '__main__':
    build_docs(
        template_path=BASE_DIR / 'deploy' / 'docs_template.txt',
        yaml_path=BASE_DIR / 'openapi.yaml',
        doc_path=BASE_DIR / 'data' / 'doc.html',
    )

    image_tag_commit = f'{local.env["IMAGE_NAME"]}:{local.env["TRAVIS_COMMIT"]}'
    image_tag_latest = f'{local.env["IMAGE_NAME"]}:latest'
    docker[
        'build',
        '-t', image_tag_commit,
        '-t', image_tag_latest,
        '.',
    ]()
    logger.info('Docker image was build, tags: %s', ', '.join([image_tag_commit, image_tag_latest]))

    docker[
        'login',
        '-u', local.env['DOCKER_USERNAME'],
        '-p', local.env['DOCKER_PASSWORD'],
    ]()

    docker['push', image_tag_commit]()
    logger.info('Pushed image: %s', image_tag_commit)

    docker['push', image_tag_latest]()
    logger.info('Pushed image: %s', image_tag_latest)
