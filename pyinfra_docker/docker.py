import json

from pyinfra.api.deploy import deploy
from pyinfra.api.exceptions import DeployError
from pyinfra.api.util import get_arg_value, make_hash
from pyinfra.operations import apt, files, yum
from six.moves import StringIO


def _apt_install(state, host):
    apt.packages(
        name='Install apt requirements to use HTTPS',
        packages=['apt-transport-https', 'ca-certificates'],
        update=True,
        cache_time=3600,
        state=state,
        host=host,
    )

    lsb_release = host.fact.lsb_release
    lsb_id = lsb_release['id'].lower()

    apt.key(
        name='Download the Docker apt key',
        src='https://download.docker.com/linux/{0}/gpg'.format(lsb_id),
        state=state,
        host=host,
    )

    add_apt_repo = apt.repo(
        name='Add the Docker apt repo',
        src=(
            'deb [arch=amd64] https://download.docker.com/linux/{0} {1} stable'
        ).format(lsb_id, lsb_release['codename']),
        filename='docker-ce-stable',
        state=state,
        host=host,
    )

    apt.packages(
        name='Install Docker via apt',
        packages='docker-ce',
        update=add_apt_repo.changed,  # update if we added the repo
        state=state,
        host=host,
    )


def _yum_install(state, host):
    yum.repo(
        name='Add the Docker yum repo',
        src='https://download.docker.com/linux/centos/docker-ce.repo',
        state=state,
        host=host,
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
        state=state,
        host=host,
    )


@deploy('Deploy Docker')
def deploy_docker(state=None, host=None, config=None):
    '''
    Install Docker on the target machine.

    Args:
        config: filename or dict of JSON data
    '''

    if not host.fact.deb_packages and not host.fact.rpm_packages:
        raise DeployError((
            'Neither apt or yum were found, '
            'pyinfra-docker cannot provision this machine!'
        ))

    # Install Docker w/apt or yum
    if host.fact.deb_packages:
        _apt_install(state, host)

    if host.fact.rpm_packages:
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

    if config:
        files.directory(
            name='Ensure /etc/docker exists',
            path='/etc/docker',
            state=state,
            host=host,
        )

        files.put(
            name='Upload the Docker daemon.json',
            src=config_file,
            dest='/etc/docker/daemon.json',
            state=state,
            host=host,
        )
