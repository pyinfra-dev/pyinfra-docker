from pyinfra.modules import init
from pyinfra_docker import install_docker


SUDO = True


install_docker(config={
    'dns': ['8.8.8.8', '8.8.4.4'],
    'debug': True,
})


init.service(
    'docker',
    running=True,
)
