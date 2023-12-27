"""Configure the gbif_registrar package for use."""

from json import load, dump
from os import environ


def load_configuration(configuration_file):
    """Loads the configuration file as global environment variables for use
    by the gbif_registrar functions.

    Remove these environment variables with the unload_configuration function.

    Parameters
    ----------
    configuration_file : str
        Path of the configuration file.

    Returns
    -------
    None

    Notes
    -----
    Create a template configuration file with the initialize_configuration_file
    function.

    Examples
    --------
    >>> load_configuration("configuration.json")
    """
    with open(configuration_file, "r", encoding="utf-8") as config:
        config = load(config)
        for key, value in config.items():
            environ[key] = value


def unload_configuration():
    """Removes global environment variables set by the load_configuration
    function.

    Returns
    -------
    None

    Examples
    --------
    >>> unload_configuration()
    """
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


def initialize_configuration_file(file_path):
    """Returns a template configuration file to path.

    The template configuration contains all the parameters a user needs to set
    up the gbif_registrar package for use.

    Parameters
    ----------
    file_path : str
        Path to which the configuration file will be written.

    Returns
    -------
    None
        Writes the template configuration file to disk as a .json file.

    Notes
    -----
    The configuration file is a .json file with the following keys:
        USER_NAME : str
            The username for the GBIF account.
        PASSWORD : str
            The password for the GBIF account.
        ORGANIZATION : str
            The organization key for the GBIF account.
        INSTALLATION : str
            The installation key for the GBIF account.
        GBIF_API : str
            The GBIF API endpoint.
        REGISTRY_BASE_URL : str
            The GBIF registry base URL.
        GBIF_DATASET_BASE_URL : str
            The GBIF dataset base URL.
        PASTA_ENVIRONMENT : str
            The PASTA environment base URL.

    Examples
    --------
    >>> initialize_configuration_file("configuration.json")
    """
    configuration = {
        "USER_NAME": "ws_client_demo",
        "PASSWORD": "Demo123",
        "ORGANIZATION": "0a16da09-7719-40de-8d4f-56a15ed52fb6",
        "INSTALLATION": "92d76df5-3de1-4c89-be03-7a17abad962a",
        "GBIF_API": "http://api.gbif-uat.org/v1/dataset",
        "REGISTRY_BASE_URL": "https://registry.gbif-uat.org/dataset",
        "GBIF_DATASET_BASE_URL": "https://www.gbif-uat.org/dataset",
        "PASTA_ENVIRONMENT": "https://pasta-s.lternet.edu",
    }
    with open(file_path, "w", encoding="utf-8") as config:
        dump(configuration, config, indent=4)
