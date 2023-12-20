"""Test init.py"""

from json import load
from os import environ
from gbif_registrar.configure import (
    load_configuration,
    unload_configuration,
    write_configuration,
)


def test_load_configuration_creates_environmental_varaiables():
    """Test that the load_configuration function creates global environment variables."""
    load_configuration("tests/test_config.json")
    assert environ["USER_NAME"] == "ws_client_demo"
    assert environ["PASSWORD"] == "Demo123"
    assert environ["ORGANIZATION"] == "0a16da09-7719-40de-8d4f-56a15ed52fb6"
    assert environ["INSTALLATION"] == "92d76df5-3de1-4c89-be03-7a17abad962a"
    assert environ["GBIF_API"] == "http://api.gbif-uat.org/v1/dataset"
    assert environ["REGISTRY_BASE_URL"] == "https://registry.gbif-uat.org/dataset"
    assert environ["GBIF_DATASET_BASE_URL"] == "https://www.gbif-uat.org/dataset"
    assert environ["PASTA_ENVIRONMENT"] == "https://pasta-s.lternet.edu"
    # Clean up the environment variables.
    unload_configuration()


def test_unload_configuration_removes_environmental_variables():
    """Test that the unload_configuration function removes global environment variables."""
    load_configuration("tests/test_config.json")
    unload_configuration()
    assert "USER_NAME" not in environ
    assert "PASSWORD" not in environ
    assert "ORGANIZATION" not in environ
    assert "INSTALLATION" not in environ
    assert "GBIF_API" not in environ
    assert "REGISTRY_BASE_URL" not in environ
    assert "GBIF_DATASET_BASE_URL" not in environ
    assert "PASTA_ENVIRONMENT" not in environ


def test_write_configuration(tmp_path):
    """Test that the write_configuration function writes a json file with the
    expected keys."""
    write_configuration(tmp_path / "test_config.json")
    with open(tmp_path / "test_config.json", "r", encoding="utf-8") as config:
        config = load(config)
        assert "USER_NAME" in config
        assert "PASSWORD" in config
        assert "ORGANIZATION" in config
        assert "INSTALLATION" in config
        assert "GBIF_API" in config
        assert "REGISTRY_BASE_URL" in config
        assert "GBIF_DATASET_BASE_URL" in config
        assert "PASTA_ENVIRONMENT" in config
