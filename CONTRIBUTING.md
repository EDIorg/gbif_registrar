# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

## Types of Contributions

### Report Bugs

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

### Write Documentation

You can never have enough documentation! Please feel free to contribute to any
part of the documentation, such as the official docs, docstrings, or even
on the web in blog posts, articles, and such.

### Submit Feedback

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

## Repository Structure

This repository is structured as a standard Python package following the conventions outlined in the [Python Packges](https://py-pkgs.org/) guide.

## Git Structure

The active branch is `development`. `development` is merged into `main` for releases. Please submit your pull requests to `development`.

## Git Commit Guidelines

This project uses Python Semantic Release, which requires the Angular commit style. For guidance, see: https://py-pkgs.org/07-releasing-versioning.html#automatic-version-bumping.

## Testing

Any new feature or bug-fix should include a unit-test demonstrating the change. Unit tests follow the [pytest](https://docs.pytest.org) framework with files in tests/. Please make sure that the testing suite passes before issuing a pull request. 

This package uses GitHub Actions continuous testing mechanism to ensure that the test suite is run on each pull request to `development` and `main`.

## Style and Formatting

This project uses [Black](https://black.readthedocs.io/en/stable/) for code formatting, and [NumPy](https://numpydoc.readthedocs.io/en/latest/format.html#style-guide) conventions for docstrings.

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
    
    > Note, this project uses Python Semantic Release, which requires the Angular commit style. For guidance, see: https://py-pkgs.org/07-releasing-versioning.html#automatic-version-bumping

4. When you're done making changes, check that your changes conform to any code formatting requirements and pass any tests.

5. Commit your changes and open a pull request.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include additional tests if appropriate.
2. If the pull request adds functionality, the docs should be updated.
3. The pull request should work for all currently supported operating systems and versions of Python.

## Code of Conduct

Please note that the `gbif_registrar` project is released with a
Code of Conduct. By contributing to this project you agree to abide by its terms.
