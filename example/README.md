# pyinfra-docker Example

Targets latest distributions: Ubuntu 16, Debian 8 and CentOS 7.

## Quickstart

Requirements:

+ [Vagrant](https://vagrantup.com)
+ [pyinfra](https://github.com/Fizzadar/pyinfra) >= 0.5

```sh
# Bring up the VMs
vagrant up

# Deploy an etcd cluster on them
pyinfra @vagrant deploy.py
```
