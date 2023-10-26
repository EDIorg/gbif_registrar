"""Initialize the gbif_registrar package."""
from json import load, dump
from os import environ


def login(configuration_file):
    """Authenticates the user with the GBIF API and sets other global
    environment variables for use by the gbif_registrar package.

    To remove these environment variables, use the logout function.

    Parameters
    ----------
    configuration_file : str
        Path of the configuration file. Create this file using the
        write_configuration function.

    Returns
    -------
    None
    """
    with open(configuration_file, "r") as config:
        config = load(config)
        for key, value in config.items():
            environ[key] = value


def logout():
    """Removes global environment variables set by the login function.

    Returns
    -------
    None
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


def write_configuration(file_path):
    """Write the template configuration to file.

    Parameters
    ----------
    file_path : str
        Path to the configuration file.

    Returns
    -------
    None
        Writes the configuration file to disk.
    """
    configuration = {
        "USER_NAME": "ws_client_demo",
        "PASSWORD": "Demo123",
        "ORGANIZATION": "0a16da09-7719-40de-8d4f-56a15ed52fb6",
        "INSTALLATION": "92d76df5-3de1-4c89-be03-7a17abad962a",
        "GBIF_API": "http://api.gbif-uat.org/v1/dataset",
        "REGISTRY_BASE_URL": "https://registry.gbif-uat.org/dataset",
        "GBIF_DATASET_BASE_URL": "https://www.gbif-uat.org/dataset",
        "PASTA_ENVIRONMENT": "https://pasta-s.lternet.edu"
    }
    # Write configuration to json file
    with open(file_path, "w") as config:
        dump(configuration, config, indent=4)
