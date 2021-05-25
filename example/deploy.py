from pyinfra.operations import server
from pyinfra_docker import deploy_docker


SUDO = True


deploy_docker(config={
    'dns': ['8.8.8.8', '8.8.4.4'],
    'debug': True,
})


server.service(
    'docker',
    running=True,
)
