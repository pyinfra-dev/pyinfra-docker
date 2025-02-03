# pyinfra Docker

A basic [pyinfra](https://pyinfra.com) deploy that installs and optionally configures Docker on the target hosts. Officially tested & supported Linux distributions:

+ Ubuntu 20/22/24
+ Debian 11/12
+ Almalinux 9

This deploy installs packages in the `docker-ce` ecosystem (`docker-ce`/`docker-ce-cli`/`docker-ce-rootless-extras`) You can specify `docker_version` in the host data and it will install that version for all `docker-ce` packages.

## Usage

See [the example](https://github.com/Fizzadar/pyinfra-docker/tree/master/example) for a more complete example.

```py
from pyinfra_docker import deploy_docker
deploy_docker()
```
