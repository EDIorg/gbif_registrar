# Contributing to gbif_registrar

The goal of `gbif_registrar` is to help the EDI data repository register datasets with GBIF and keep them up-to-date. Any task related process is supported.

We welcome community contributions to this work.

## Development and Release Process

The `main` branch always reflects the current stable release, a `development` branch is used for merging features, and `feature` branches create changes. Once a feature passes review, it's commit history is squashed and commit title, following the [Angular commit style](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#-commit-message-format), is added along with reference to the issue it closes. The feature is merged into `development`. `development` is reviewed before each release, and upon approval is merged into `main`. 

Merges to `main` kick-off a GitHub Action workflow in which Python Semantic Release bumps the version number, tags the release, and builds the changelog. Additionally, the workflow updates package documentation, creates a downloadable release on GitHub, and archives it with Zenodo. Finally, the changes introduced to `main` during the release process are merged back into `development` to keep the branches synchronized.

## Types of Contributions

### Report Bugs

Bug reports are always appreciated. If you are reporting a bug, please use the "Bug report" issue template.

### Propose Features

If you are proposing a feature, please use the "Feature request" issue template.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.

### Write Documentation

Please feel free to contribute to any part of the documentation, such as the official docs, docstrings, or even
on the web in blog posts, articles, and such.

## Repository Structure

This repository is structured as a standard Python package following the conventions outlined in the [Python Packges](https://py-pkgs.org/) guide.

## Git Commit Guidelines

This project uses Python Semantic Release to streamline the deployment process. As a consequence, the [Angular commit style](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#-commit-message-format) is required. 

Issues corresponding to a commit should be referenced at the end of the commit message title line. For example, `feat: add framework for new feature (#3, #5)`. This provides readers helpful context for interpreting the changelog.

## Testing

Any new feature or bug-fix should include a unit-test demonstrating the change. Unit tests follow the [pytest](https://docs.pytest.org) framework with files in tests/. Please make sure that the testing suite passes before issuing a pull request. 

This package uses GitHub Actions continuous testing mechanism to ensure that the test suite is run on each pull request to `development` and `main`.

## Style and Formatting

This project uses [Black](https://black.readthedocs.io/en/stable/) for code formatting, [Pylint](https://pylint.pycqa.org/en/latest/) for static code analysis, and [NumPy](https://numpydoc.readthedocs.io/en/latest/format.html#style-guide) conventions for docstrings. Black is strictly enforced by the CI/CD GitHub Action Workflow but Pylint is not.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include additional tests if appropriate.
2. If the pull request adds functionality, the docs should be updated.
3. The pull request should be made to the `development` branch.

Notes for project maintainers:
- Pull requests should be reviewed for use of the [Angular commit style](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#-commit-message-format). If styling is absent, it can be added by the maintainer as a summarizing commit title of the squash and merge option.
- Pull requests should always be rebased and merged (preferably) or squashed and merged onto the development branch to preserve a linear commit history and to make commit messages, in the [Angular commit style](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#-commit-message-format), actionable by the semantic release process.

## Get Started!

Ready to contribute? Here's how to set up `gbif_registrar` for local development.

1. Download a copy of `gbif_registrar` locally.
2. Install `gbif_registrar` using `poetry`:

    ```console
    $ poetry install
    ```

3. Use `git` (or similar) to create a branch for local development and make your changes:

    ```console
    $ git checkout -b name-of-your-bugfix-or-feature
    ```

4. When you're done making changes, check that your changes conform to any code formatting requirements and pass any tests.

5. Commit your changes using our Git Commit Guidelines (see above). The commit should include reference to any related issues.

6. Open a pull request following the Pull Request Guidelines (see above).

## Code of Conduct

Please note that the `gbif_registrar` project is released with a [Code of Conduct](https://github.com/clnsmth/gbif_registrar/blob/main/CONDUCT.md). By contributing to this project you agree to abide by its terms.