testinfra_hosts = [
    "ssh://ubuntu20",
    "ssh://ubuntu22",
    "ssh://ubuntu24",
    "ssh://debian11",
    "ssh://debian12",
    "ssh://almalinux9",
]


def test_docker_running_and_enabled(host):
    docker = host.service("docker")
    assert docker.is_running
    assert docker.is_enabled
