from io import open

from setuptools import find_packages, setup


with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()


if __name__ == '__main__':
    setup(
        version='1.0',
        name='pyinfra-docker',
        description='Install & configure Docker with `pyinfra`.',
        long_description=readme,
        long_description_content_type='text/markdown',
        url='https://github.com/Fizzadar/pyinfra-docker',
        author='Nick / Fizzadar',
        author_email='pointlessrambler@gmail.com',
        license='MIT',
        packages=find_packages(),
        install_requires=('pyinfra>=1',),
        include_package_data=True,
    )
