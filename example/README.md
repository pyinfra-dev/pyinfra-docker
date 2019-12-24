# pyinfra-docker Example

Targets distributions: Ubuntu 16/18, Debian 9/10 and CentOS 7.

Note: Could not get docker-ce to work on Centos8.

## Quickstart

Requirements:

+ [Vagrant](https://vagrantup.com)
+ [pyinfra](https://github.com/Fizzadar/pyinfra) >= 0.5

```sh
# Bring up the virtual machine instances
vagrant up

# Create a python virtual environment for pyinfra using python3
virtualenv -p python3 venv

# Activate python virtual environment
source venv/bin/activate

# Install pyinfra into the python virtual environment
pip install pyinfra

# Install pyinfra-docker into the python virtual environment
cd ..
python setup.py install

# Deploy docker to each virtual machine
cd example
pyinfra @vagrant deploy.py
```
