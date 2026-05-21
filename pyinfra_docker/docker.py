import json
from io import StringIO

from pyinfra.api.deploy import deploy
from pyinfra.api.exceptions import DeployError
from pyinfra.api.util import make_hash
from pyinfra.context import host
from pyinfra.facts.server import Command, LinuxName, OsRelease, Which
from pyinfra.operations import apt, dnf, files, gpg

DEFAULTS = {
    "docker_version": None,
}


def get_pkgs_to_install(operator):
    docker_packages = [
        "docker-ce",
        "docker-ce-cli",
        "docker-ce-rootless-extras",
        "docker-compose-plugin"
    ]
    if not host.data.docker_version:
        return docker_packages

    return [f"{pkg}{operator}{host.data.docker_version}" for pkg in docker_packages]


def _apt_install(packages):
    apt.packages(
        name="Install Script Dependencies",
        packages=["apt-transport-https", "ca-certificates", "curl", "gnupg", "lsb-release"],
        update=True,
        cache_time=3600,
    )

    os_release = host.get_fact(OsRelease)
    lsb_id = os_release["id"].lower()

    keyringPath = "/etc/apt/keyrings"
    gpgKeyPath = f"{keyringPath}/docker.asc"

    files.directory(
        name="Ensure Keyrings Directory Exists",
        path=keyringPath,
        present=True,
        mode="0755",
        force=True,
    )

    key = gpg.key(
        name=f"Download GPG Key for distribution {lsb_id}",
        src=f"https://download.docker.com/linux/{lsb_id}/gpg",
        dest=gpgKeyPath,
    )

    lsb_id = os_release["id_like"].split()[0].lower()
    gpg.key(
        name=f"Download GPG Key for distribution {lsb_id}",
        src=f"https://download.docker.com/linux/{lsb_id}/gpg",
        dest=gpgKeyPath,
        _if=key.did_error,
    )

    dpkg_arch = host.get_fact(Command, command="dpkg --print-architecture")

    add_apt_repo = apt.repo(
        name="Add the Docker APT repo",
        src=(
            f"deb [arch={dpkg_arch} signed-by={gpgKeyPath}] https://download.docker.com/linux/{lsb_id}"
            f" {os_release['version_codename']} stable"
        ),
        filename="docker",
    )

    apt.packages(
        name="Install Docker via APT",
        packages=packages,
        update=add_apt_repo.changed,  # update if we added the repo
        allow_downgrades=True,
    )


def _dnf_install(packages):
    linuxName = host.get_fact(LinuxName).lower()

    osOverrides = {"almalinux": "rhel"}

    if linuxName in osOverrides:
        linuxName = osOverrides[linuxName]

    add_dnf_repo = dnf.repo(
        name="Add the Docker DNF repo",
        src=f"https://download.docker.com/linux/{linuxName}/docker-ce.repo",
        present=True,
    )

    dnf.packages(
        name="Install Docker via DNF",
        packages=packages,
        present=True,
        update=add_dnf_repo.changed,
    )


@deploy("Deploy Docker", data_defaults=DEFAULTS)
def deploy_docker(config=None):
    """
    Install Docker on the target machine.

    Args:
        config: filename or dict of JSON data
    """
    if host.get_fact(Which, command="apt") is not None:
        packages = get_pkgs_to_install("=")
        _apt_install(packages)
    elif host.get_fact(Which, command="dnf") is not None:
        packages = get_pkgs_to_install("-")
        _dnf_install(packages)
    else:
        raise DeployError(
            (
                "Neither apt or dnf were found, "
                f"pyinfra-docker cannot provision this machine! {host.name}"
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
