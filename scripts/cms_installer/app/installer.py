import re
from pathlib import Path
from typing import Container

import docker
from docker import DockerClient
from docker.models.images import Image

installer_regex = re.compile(r".+/install:.+")


class DockerClientFactory:
    _docker_client = None
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._docker_client = docker.from_env()
        return cls._instance

    def get(self) -> DockerClient:
        return self._docker_client


def get_installer_images() -> list[Image]:
    docker_client = DockerClientFactory().get()
    return [
        img for img in docker_client.images.list() if installer_regex.match(img.tags[0])
    ]


def load_installer_image(path_to_tar_file: Path):
    docker_client = DockerClientFactory().get()
    with open(path_to_tar_file, "rb") as f:
        docker_client.images.load(f)


def run_installer_container() -> Container:
    docker_client = DockerClientFactory().get()
    images = get_installer_images()
    if len(images) == 0:
        raise RuntimeError("No installer images found")
    elif len(images) > 1:
        raise RuntimeError("Multiple installer images found")
    image = images[0]
    return docker_client.containers.run(image.id, command=["tail", "-f", "/dev/null"])
