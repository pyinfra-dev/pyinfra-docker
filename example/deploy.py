from pyinfra.operations import init
from pyinfra_docker import deploy_docker


SUDO = True


deploy_docker(config={
    'dns': ['8.8.8.8', '8.8.4.4'],
    'debug': True,
})


init.service(
    'docker',
    running=True,
)
