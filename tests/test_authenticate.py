"""Test init.py"""
from os import environ
from gbif_registrar.authenticate import login
from gbif_registrar.authenticate import logout


def test_login_creates_environmental_varaiables():
    """Test that the login function creates global environment variables."""
    # Read the configuration file.
    login("tests/config.json")
    # Check that the global environment variables are set as expected.
    assert environ["USER_NAME"] == "ws_client_demo"
    assert environ["PASSWORD"] == "Demo123"
    assert environ["ORGANIZATION"] == "0a16da09-7719-40de-8d4f-56a15ed52fb6"
    assert environ["INSTALLATION"] == "92d76df5-3de1-4c89-be03-7a17abad962a"
    assert environ["GBIF_API"] == "http://api.gbif-uat.org/v1/dataset"
    assert environ["REGISTRY_BASE_URL"] == "https://registry.gbif-uat.org/dataset"
    assert environ["GBIF_DATASET_BASE_URL"] == "https://www.gbif-uat.org/dataset"
    assert environ["PASTA_ENVIRONMENT"] == "https://pasta-s.lternet.edu"
    # Clean up the environment variables.
    logout()


def test_logout_removes_environmental_variables():
    """Test that the logout function removes global environment variables."""
    login("tests/config.json")
    logout()
    # Check that the global environment variables are removed as expected.
    assert "USER_NAME" not in environ
    assert "PASSWORD" not in environ
    assert "ORGANIZATION" not in environ
    assert "INSTALLATION" not in environ
    assert "GBIF_API" not in environ
    assert "REGISTRY_BASE_URL" not in environ
    assert "GBIF_DATASET_BASE_URL" not in environ
    assert "PASTA_ENVIRONMENT" not in environ
