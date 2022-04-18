from io import open

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

if __name__ == "__main__":
    setup(
        version="2.0",
        name="pyinfra-docker",
        description="Install & configure Docker with `pyinfra`.",
        long_description=readme,
        long_description_content_type="text/markdown",
        url="https://github.com/Fizzadar/pyinfra-docker",
        author="Nick / Fizzadar",
        author_email="nick@fizzadar.com",
        license="MIT",
        packages=find_packages(),
        install_requires=("pyinfra>=2,<3",),
        extras_require={
            "test": [
                "pytest",
                "pytest-testinfra",
            ],
            "lint": [
                "black",
                "isort",
                "flake8",
                "flake8-black",
                "flake8-isort",
                "flake8-commas",
            ],
        },
        include_package_data=True,
    )
