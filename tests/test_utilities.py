"""Test utilities"""
import os.path
import hashlib
import pytest
import pandas as pd
from gbif_registrar.utilities import read_registrations
from gbif_registrar.utilities import initialize_registrations
from gbif_registrar.utilities import expected_cols
from gbif_registrar.utilities import read_local_dataset_metadata
from gbif_registrar.utilities import has_metadata
from gbif_registrar.utilities import get_gbif_dataset_details


@pytest.fixture(name="eml")
def eml_fixture():
    """Create an EML XML string for testing."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <eml:eml packageId="knb-lter-ble.20.1" system="https://pasta-d.lternet.edu" 
    xmlns:eml="eml://ecoinformatics.org/eml-2.1.1" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:schemaLocation="eml://ecoinformatics.org/eml-2.1.1 
    https://pasta.lternet.edu/eml/eml-2.1.1.xsd">
        <dataset>
            <title>Long-term monitoring of the effects of prescribed fire on the structure, composition, and function of upland pine-dominated forests at the Santee Experimental Forest, South Carolina, USA (1989 to present)</title>
            <pubDate>2019-08-01</pubDate>
        </dataset>
    </eml:eml>
    """
    return xml_content


def test_initialize_registrations_writes_to_path(tmp_path):
    """File is written to path."""
    file = tmp_path / "registrations.csv"
    initialize_registrations(file)
    assert os.path.exists(file)


def test_initialize_registrations_does_not_overwrite(tmp_path):
    """Does not overwrite."""
    file = tmp_path / "registrations.csv"
    initialize_registrations(file)
    with open(file, "rb") as rgstrs:
        md5_before = hashlib.md5(rgstrs.read()).hexdigest()
    with open(file, "rb") as rgstrs:
        md5_after = hashlib.md5(rgstrs.read()).hexdigest()
    assert md5_before == md5_after


def test_initialize_registrations_has_expected_columns(tmp_path):
    """Has expected columns."""
    file = tmp_path / "registrations.csv"
    initialize_registrations(file)
    data = pd.read_csv(file, delimiter=",")
    missing_cols = not set(expected_cols()).issubset(set(data.columns))
    assert not missing_cols


def test_read_registrations_reads_file():
    """Reads the file."""
    rgstrs = read_registrations("tests/registrations.csv")
    assert isinstance(rgstrs, pd.DataFrame)


def test_read_registrations_formats_datetime():
    """Formats the datetime column."""
    rgstrs = read_registrations("tests/registrations.csv")
    crawl_time = rgstrs["gbif_endpoint_set_datetime"]
    assert pd.core.dtypes.common.is_datetime64_dtype(crawl_time)


def test_read_local_dataset_metadata_success(mocker, eml):
    """Test that read_local_dataset_metadata returns a string on success."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = eml
    mocker.patch("requests.get", return_value=mock_response)
    metadata = read_local_dataset_metadata("knb-lter-ble.20.1")
    assert isinstance(metadata, str)


def test_read_local_dataset_metadata_failure(mocker):
    """Test that read_local_dataset_metadata returns None on failure."""
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.reason = "Not Found"
    mocker.patch("requests.get", return_value=mock_response)
    metadata = read_local_dataset_metadata("knb-lter-ble.20.10")
    assert metadata is None


def test_has_metadata_success(mocker):
    """Test that has_metadata returns True on success."""
    # Create a JSON string simulating a successful response from the GBIF API
    json_content = """{"title":"This is a title"}"""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = json_content
    mocker.patch("requests.get", return_value=mock_response)
    res = has_metadata("cfb3f6d5-ed7d-4fff-9f1b-f032ed1de485")
    assert isinstance(res, bool)


def test_has_metadata_failure(mocker):
    """Test that has_metadata returns False on failure.

    Failure may occur if the GBIF API returns a 404 status code or if the
    JSON response doesn't contain a title."""

    # Case 1: GBIF API returns a 404 status code
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.reason = "Not Found"
    mocker.patch("requests.get", return_value=mock_response)
    res = has_metadata("cfb3f6d5-ed7d-4fff-9f1b-f032ed1de485")
    assert res is False

    # Case 2: GBIF API returns a 200 status code but the JSON response doesn't
    # contain a title
    json_content = """{"description":"This is a description"}"""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = json_content
    mocker.patch("requests.get", return_value=mock_response)
    res = has_metadata("cfb3f6d5-ed7d-4fff-9f1b-f032ed1de485")
    assert res is False


def test_get_gbif_dataset_details_success(mocker):
    """Test that get_gbif_dataset_details returns a dict on success."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = """{"title":"This is a title"}"""
    mocker.patch("requests.get", return_value=mock_response)
    res = get_gbif_dataset_details("cfb3f6d5-ed7d-4fff-9f1b-f032ed1de485")
    assert isinstance(res, dict)


def test_get_gbif_dataset_details_failure(mocker):
    """Test that get_gbif_dataset_details returns None on failure."""
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.reason = "Not Found"
    mocker.patch("requests.get", return_value=mock_response)
    res = get_gbif_dataset_details("cfb3f6d5-ed7d-4fff-9f1b-f032e")
    assert res is None
