"""Initialize the gbif_registrar package."""
from json import load
from os import environ


def login(configuration_file):
    """Creates global environment variables for functions in the
    gbif_registrar package.

    To remove these environment variables, use the logout function.

    Parameters
    ----------
    configuration_file : str
        Path of the configuration file.

    Returns
    -------
    None
    """
    # Read the .json configuration file.
    with open(configuration_file, "r") as config:
        config = load(config)
        # Iterate over the configuration file and set the global environment
        # variables.
        for key, value in config.items():
            environ[key] = value


def logout():
    """Removes global environment variables set by the login function.

    Returns
    -------
    None
    """
    # Iterate over the list of configuration variables and remove them from
    # the global environment.
    env_vars = [
        "USER_NAME",
        "PASSWORD",
        "ORGANIZATION",
        "INSTALLATION",
        "GBIF_API",
        "REGISTRY_BASE_URL",
        "GBIF_DATASET_BASE_URL",
        "PASTA_ENVIRONMENT",
    ]
    for key in env_vars:
        del environ[key]
