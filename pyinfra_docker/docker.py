import json
from io import StringIO

from pyinfra import host
from pyinfra.api.deploy import deploy
from pyinfra.api.exceptions import DeployError
from pyinfra.api.util import make_hash
from pyinfra.facts.deb import DebPackages
from pyinfra.facts.rpm import RpmPackages
from pyinfra.facts.server import LsbRelease
from pyinfra.operations import apt, files, yum


def _apt_install():
    apt.packages(
        name='Install apt requirements to use HTTPS',
        packages=['apt-transport-https', 'ca-certificates'],
        update=True,
        cache_time=3600,
    )

    lsb_release = host.get_fact(LsbRelease)
    lsb_id = lsb_release['id'].lower()

    apt.key(
        name='Download the Docker apt key',
        src='https://download.docker.com/linux/{0}/gpg'.format(lsb_id),
    )

    add_apt_repo = apt.repo(
        name='Add the Docker apt repo',
        src=(
            'deb [arch=amd64] https://download.docker.com/linux/{0} {1} stable'
        ).format(lsb_id, lsb_release['codename']),
        filename='docker-ce-stable',
    )

    apt.packages(
        name='Install Docker via apt',
        packages='docker-ce',
        update=add_apt_repo.changed,  # update if we added the repo
    )


def _yum_install():
    yum.repo(
        name='Add the Docker yum repo',
        src='https://download.docker.com/linux/centos/docker-ce.repo',
    )

    # Installing Docker on CentOS 8 is currently broken and requires this hack
    # See: https://github.com/docker/for-linux/issues/873
    extra_install_args = ''
    linux_distro = host.fact.linux_distribution
    if linux_distro['name'] == 'CentOS' and linux_distro['major'] == 8:
        extra_install_args = '--nobest'

    yum.packages(
        name='Install Docker via yum',
        packages=['docker-ce'],
        extra_install_args=extra_install_args,
    )


@deploy('Deploy Docker')
def deploy_docker(config=None):
    '''
    Install Docker on the target machine.

    Args:
        config: filename or dict of JSON data
    '''

    if not host.get_fact(DebPackages) and not host.get_fact(RpmPackages):
        raise DeployError((
            'Neither apt or yum were found, '
            'pyinfra-docker cannot provision this machine!'
        ))

    # Install Docker w/apt or yum
    if host.get_fact(DebPackages):
        _apt_install()

    if host.get_fact(RpmPackages):
        _yum_install()

    config_file = config

    # If config is a dictionary, turn it into a JSON file for the config
    if isinstance(config, dict):
        config_hash = make_hash(config)

        # Turn into a file-like object and name such that we only generate one
        # operation hash between multiple hosts (with the same config).
        config_file = StringIO(json.dumps(config))
        config_file.__name__ = config_hash

    if config:
        files.directory(
            name='Ensure /etc/docker exists',
            path='/etc/docker',
        )

        files.put(
            name='Upload the Docker daemon.json',
            src=config_file,
            dest='/etc/docker/daemon.json',
        )
