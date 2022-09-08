# Install and development tips

All the development dependencies are declared at [dev-requirements.txt](dev-requirements.txt).

```bash
python3 -m venv .pyenv
source .pyenv/bin/activate
pip install --upgrade pip wheel
pip install -r dev-requirements.txt
```

One of these dependencies is [pre-commit](https://pre-commit.com/), whose rules are declared at [.pre-commit-config.yaml](.pre-commit-config.yaml).

The rules run both [pylint](https://pypi.org/project/pylint/),
[mypy](http://mypy-lang.org/) and [black](https://black.readthedocs.io/en/stable/).

The pre-commit development hook which runs these tools before any commit is installed just running:

```bash
pre-commit install
```

If you want to explicitly run the hooks at any moment, even before doing the commit itself, you only have to run:

```bash
pre-commit run -a
```

As these checks are applied only to the python version currently being used in the development,
there is a GitHub workflow at [.github/workflows/pre-commit.yml](.github/workflows/pre-commit.yml)
which runs them on several Python versions.

If you have lots of cores, fast disks and docker installed, you can locally run the pre-commit GitHub workflow using [act](https://github.com/nektos/act):

```bash
act -j pre-commit
```
