from pyinfra import config
from pyinfra.operations import server

from pyinfra_docker import deploy_docker

config.SUDO = True


deploy_docker(
    config={
        "dns": ["8.8.8.8", "8.8.4.4"],
        "debug": True,
    },
)


server.service(
    name="Ensure docker service is running",
    service="docker",
    running=True,
    enabled=True,
)
