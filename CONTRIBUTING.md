# Contributor Guide

Thank you for your interest in improving this project.
This project is open-source under the [MIT license] and
welcomes contributions in the form of bug reports, feature requests, and pull requests.

Here is a list of important resources for contributors:

- [Source Code]
- [Documentation]
- [Issue Tracker]
- [Code of Conduct]

## How to report a bug

Report bugs on the [Issue Tracker].

When filing an issue, make sure to answer these questions:

- Which operating system and Python version are you using?
- Which version of this project are you using?
- What did you do?
- What did you expect to see?
- What did you see instead?

The best way to get your bug fixed is to provide a test case,
and/or steps to reproduce the issue.

## How to request a feature

Request features on the [Issue Tracker].

## How to set up your development environment

You need Python 3.12+ and the following tools:

- [uv]
- [Nox]

Install [pipx]:

```console
python -m pip install --user pipx
python -m pipx ensurepath
```

Install [uv]:

<https://docs.astral.sh/uv/getting-started/installation/>

```console
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install [Nox]:

```console
pipx install nox
```

Install the pre-commit hooks

```console
nox --session=pre-commit -- install
```

Install the package with development requirements:

```console
uv sync --dev
```

You can now run datadoc:

```console
uv run datadoc
```

## Config for local development

We use a python package called `python-dotenv` for configuration management. This gives two possibilities for sourcing configuration:

1. Environment variables.
1. A file called `.env` by convention.

To set up for local development run this command from the root of the repo.

1. Create a file `src/datadoc_editor/.env`
1. Place the following lines in the file:

   ```env
   DATADOC_DASH_DEVELOPMENT_MODE=True
   DATADOC_LOG_LEVEL=debug
   ```

To see all configuration options, see `src/datadoc_editor/config.py`

## How to test the project

Run the full test suite:

```console
nox
```

List the available Nox sessions:

```console
nox --list-sessions
```

You can also run a specific Nox session.
For example, invoke the unit test suite like this:

```console
nox --session=tests
```

Unit tests are located in the _tests_ directory,
and are written using the [pytest] testing framework.

## Running the Dockerized Application Locally

```bash
docker run -p 8050:8050 \
-v $HOME/.config/gcloud/application_default_credentials.json/:/application_default_credentials.json \
-e GOOGLE_APPLICATION_CREDENTIALS="/application_default_credentials.json" \
datadoc
```

## Release process

Update the version using `uv version --bump`. This project follows [semantic versioning](https://semver.org/):

```bash
uv version --bump patch   # bug fixes
uv version --bump minor   # new features
uv version --bump major   # breaking changes
```

Create a new branch for the release.

Commit with message like `Bump version x.x.x -> y.y.y`.

Open and merge a PR.

## How to submit changes

Open a [pull request] to submit changes to this project.

Your pull request needs to meet the following guidelines for acceptance:

- The Nox test suite must pass without errors and warnings.
- Include unit tests. This project maintains 100% code coverage.
- If your changes add functionality, update the documentation accordingly.

Feel free to submit early, though—we can always iterate on this.

To run linting and code formatting checks before committing your change, you can install pre-commit as a Git hook by running the following command:

```console
nox --session=pre-commit -- install
```

It is recommended to open an issue before starting work on anything.
This will allow a chance to talk it over with the owners and validate your approach.

[mit license]: https://opensource.org/licenses/MIT
[source code]: https://github.com/statisticsnorway/datadoc
[documentation]: https://statisticsnorway.github.io/datadoc
[issue tracker]: https://github.com/statisticsnorway/datadoc-editor/issues
[pipx]: https://pipx.pypa.io/
[nox]: https://nox.thea.codes/
[pytest]: https://pytest.readthedocs.io/
[pull request]: https://github.com/statisticsnorway/datadoc-editor/pulls

<!-- github-only -->

[code of conduct]: CODE_OF_CONDUCT.md
