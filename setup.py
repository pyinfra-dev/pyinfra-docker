from setuptools import find_packages, setup


if __name__ == '__main__':
    setup(
        version='0.1',
        name='pyinfra-docker',
        packages=find_packages(),
        install_requires=('pyinfra>=0.5',),
    )
