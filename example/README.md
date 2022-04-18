# pyinfra-docker Example

See [`deploy.py`](./deploy.py) for example code to use `pyinfra-docker`.

## Quickstart

You will need [Vagrant](https://vagrantup.com) installed.

```sh
# Bring up the virtual machine instances
vagrant up

# Install pyinfra-docker + pyinfra dependency
pip install -e '../'

# Deploy docker to each virtual machine
pyinfra @vagrant deploy.py
```

## Tests

```sh
# Ensure we have test packages installed
pip install -e '../[test]'

# Dump vagrant SSH config
vagrant ssh-config > ssh_config

# Run pytest
pytest --ssh-config ssh_config tests.py
```
