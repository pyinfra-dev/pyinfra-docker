testinfra_hosts = [
    "ssh://ubuntu16",
    "ssh://ubuntu18",
    "ssh://ubuntu20",
    "ssh://debian9",
    "ssh://debian10",
    "ssh://centos7",
    "ssh://almalinux8",
]


def test_docker_running_and_enabled(host):
    docker = host.service("docker")
    assert docker.is_running
    assert docker.is_enabled
