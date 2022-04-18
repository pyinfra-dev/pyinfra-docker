import json
from io import StringIO

from pyinfra import host
from pyinfra.api.deploy import deploy
from pyinfra.api.exceptions import DeployError
from pyinfra.api.util import make_hash
from pyinfra.facts.deb import DebPackages
from pyinfra.facts.rpm import RpmPackages
from pyinfra.facts.server import Command, LinuxDistribution, LsbRelease, Which
from pyinfra.operations import apt, dnf, files, yum


def _apt_install():
    apt.packages(
        name="Install apt requirements to use HTTPS",
        packages=["apt-transport-https", "ca-certificates"],
        update=True,
        cache_time=3600,
    )

    lsb_release = host.get_fact(LsbRelease)
    lsb_id = lsb_release["id"].lower()

    apt.key(
        name="Download the Docker apt key",
        src="https://download.docker.com/linux/{0}/gpg".format(lsb_id),
    )

    dpkg_arch = host.get_fact(Command, command="dpkg --print-architecture")

    add_apt_repo = apt.repo(
        name="Add the Docker apt repo",
        src=(
            f"deb [arch={dpkg_arch}] https://download.docker.com/linux/{lsb_id}"
            f" {lsb_release['codename']} stable"
        ),
        filename="docker-ce-stable",
    )

    apt.packages(
        name="Install Docker via apt",
        packages="docker-ce",
        update=add_apt_repo.changed,  # update if we added the repo
    )


def _yum_or_dnf_install(yum_or_dnf):
    yum_or_dnf.repo(
        name="Add the Docker yum repo",
        src="https://download.docker.com/linux/centos/docker-ce.repo",
    )

    # Installing Docker on CentOS 8 is currently broken and requires this hack
    # See: https://github.com/docker/for-linux/issues/873
    extra_install_args = ""
    linux_distro = host.get_fact(LinuxDistribution)
    if linux_distro["name"] == "CentOS" and linux_distro["major"] == 8:
        extra_install_args = "--nobest"

    yum_or_dnf.packages(
        name="Install Docker via yum",
        packages=["docker-ce"],
        extra_install_args=extra_install_args,
    )


@deploy("Deploy Docker")
def deploy_docker(config=None):
    """
    Install Docker on the target machine.

    Args:
        config: filename or dict of JSON data
    """

    if host.get_fact(DebPackages):
        _apt_install()
    elif host.get_fact(RpmPackages):
        _yum_or_dnf_install(
            dnf if host.get_fact(Which, command="dnf") else yum,
        )
    else:
        raise DeployError(
            (
                "Neither apt or yum were found, "
                "pyinfra-docker cannot provision this machine!"
            ),
        )

    config_file = config

    # If config is a dictionary, turn it into a JSON file for the config
    if isinstance(config, dict):
        config_hash = make_hash(config)

        # Turn into a file-like object and name such that we only generate one
        # operation hash between multiple hosts (with the same config).
        config_file = StringIO(json.dumps(config, indent=4))
        config_file.__name__ = config_hash

    if config:
        files.put(
            name="Upload the Docker daemon.json",
            src=config_file,
            dest="/etc/docker/daemon.json",
        )
