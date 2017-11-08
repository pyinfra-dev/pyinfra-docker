# pyinfra-docker
# File: pyinfra_docker/docker.py
# Desc: install Docker with pyinfra using apt or yum

import json

from pyinfra.api.deploy import deploy
from pyinfra.api.exceptions import DeployError
from pyinfra.api.util import get_arg_value, make_hash
from pyinfra.modules import apt, files, yum
from six.moves import StringIO


def _apt_install(state, host):
    apt.packages(
        state, host,
        {'Install apt requirements to use HTTPS'},
        ['apt-transport-https', 'ca-certificates'],
    )

    apt.key(
        state, host,
        {'Download the Docker apt key'},
        (
            'https://download.docker.com/linux/'
            '{{ host.fact.lsb_release.id|lower }}/gpg'
        ),
    )

    add_apt_repo = apt.repo(
        state, host,
        {'Add the Docker apt repo'},
        (
            'deb [arch=amd64] https://download.docker.com/linux/'
            '{{ host.fact.lsb_release.id|lower }} '
            '{{ host.fact.lsb_release.codename }} stable'
        ),
        filename='docker-ce-stable',
    )

    apt.packages(
        state, host,
        {'Install Docker via apt'},
        'docker-ce',
        # Update apt if we added the repo
        update=add_apt_repo.changed,
    )


def _yum_install(state, host):
    yum.repo(
        state, host,
        {'Add the Docker yum repo'},
        'docker-ce-stable',
        'https://download.docker.com/linux/centos/7/$basearch/stable',
        description='Docker CE Stable - $basearch',
        gpgkey='https://download.docker.com/linux/centos/gpg',
    )

    yum.packages(
        state, host,
        {'Install Docker via yum'},
        'docker-ce',
    )


@deploy('Deploy Docker')
def deploy_docker(state, host, config=None):
    '''
    Install Docker on the target machine.

    Args:
        config: filename or dict of JSON data
    '''

    # Fail early!
    if not host.fact.deb_packages and not host.fact.rpm_packages:
        raise DeployError((
            'Neither apt or yum were found, '
            'pyinfra-docker cannot provision this machine!'
        ))

    # Install Docker w/apt or yum
    with state.when(host.fact.deb_packages):
        _apt_install(state, host)

    with state.when(host.fact.rpm_packages):
        _yum_install(state, host)

    config_file = config

    # If config is a dictionary, turn it into a JSON file for the config
    if isinstance(config, dict):
        config_hash = make_hash(config)

        # Convert any jinja2 string variables ({{ host.data...}})
        config = get_arg_value(state, host, config)

        # Turn into a file-like object and name such that we only generate one
        # operation hash between multiple hosts (with the same config).
        config_file = StringIO(json.dumps(config))
        config_file.__name__ = config_hash

    with state.when(config):
        files.directory(
            state, host,
            {'Ensure /etc/docker exists'},
            '/etc/docker',
        )

        files.put(
            state, host,
            {'Upload the Docker daemon.json'},
            config_file,
            '/etc/docker/daemon.json',
        )
