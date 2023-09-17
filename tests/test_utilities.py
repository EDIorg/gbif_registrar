"""Test utilities"""
import os.path
import hashlib
from json import loads
import pytest
import pandas as pd
from gbif_registrar.utilities import read_registrations
from gbif_registrar.utilities import initialize_registrations
from gbif_registrar.utilities import expected_cols
from gbif_registrar.utilities import read_local_dataset_metadata
from gbif_registrar.utilities import has_metadata
from gbif_registrar.utilities import read_gbif_dataset_metadata
from gbif_registrar.utilities import is_synchronized


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
            <title>This is a title</title>
            <pubDate>2019-08-01</pubDate>
        </dataset>
    </eml:eml>
    """
    return xml_content


@pytest.fixture(name="gbif_metadata")
def gbif_metadata_fixture():
    """Create a dict of GBIF metadata for testing."""
    metadata = {
        "pubDate": "2019-08-01T00:00:00.000+0000",
        "endpoints": [
            {"url": "https://pasta-s.lternet.edu/package/download/eml/edi/941/3"}
        ],
    }
    return metadata


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
    mock_response = loads("""{"title":"This is a title"}""")
    mocker.patch(
        "gbif_registrar.utilities.read_gbif_dataset_metadata",
        return_value=mock_response,
    )
    res = has_metadata("cfb3f6d5-ed7d-4fff-9f1b-f032ed1de485")
    assert isinstance(res, bool)


def test_has_metadata_failure(mocker):
    """Test that has_metadata returns False on failure.

    Failure occurs if the response doesn't contain a title or the response is
    None."""

    # Case 1: Response from read_gbif_dataset_metadata doesn't contain a title
    mock_response = loads("""{"description":"This is a description"}""")
    mocker.patch(
        "gbif_registrar.utilities.read_gbif_dataset_metadata",
        return_value=mock_response,
    )
    res = has_metadata("cfb3f6d5-ed7d-4fff-9f1b-f032ed1de485")
    assert res is False

    # Case 2: Response from read_gbif_dataset_metadata is None
    mock_response = None
    mocker.patch(
        "gbif_registrar.utilities.read_gbif_dataset_metadata",
        return_value=mock_response,
    )
    res = has_metadata("cfb3f6d5-ed7d-4fff-9f1b-f032ed1de485")
    assert res is False


def test_read_gbif_dataset_metadata_success(mocker):
    """Test that read_gbif_dataset_metadata returns a dict on success."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = """{"title":"This is a title"}"""
    mocker.patch("requests.get", return_value=mock_response)
    res = read_gbif_dataset_metadata("cfb3f6d5-ed7d-4fff-9f1b-f032ed1de485")
    assert isinstance(res, dict)


def test_read_gbif_dataset_metadata_failure(mocker):
    """Test that read_gbif_dataset_metadata returns None on failure."""
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.reason = "Not Found"
    mocker.patch("requests.get", return_value=mock_response)
    res = read_gbif_dataset_metadata("cfb3f6d5-ed7d-4fff-9f1b-f032e")
    assert res is None


def test_is_synchronized_success(tmp_path, mocker, eml, gbif_metadata):
    """Test that is_synchronized returns True on success."""
    registrations = read_registrations("tests/registrations.csv")
    # Add new line to registrations with a dataset that is synchronized with
    # GBIF so that is_synchronized can access this information via the
    # file_path argument.
    local_dataset_id = "edi.941.3"
    new_row = registrations.iloc[-1].copy()
    new_row["local_dataset_id"] = local_dataset_id
    new_row["local_dataset_group_id"] = "edi.941"
    new_row["gbif_dataset_uuid"] = "cfb3f6d5-ed7d-4fff-9f1b-f032ed1de485"
    new_row[
        "local_dataset_endpoint"
    ] = "https://pasta-s.lternet.edu/package/data/eml/edi/941/3"
    registrations = registrations.append(new_row, ignore_index=True)
    registrations.to_csv(tmp_path / "registrations.csv", index=False)

    # Mock the response from read_local_dataset_metadata and
    # read_gbif_dataset_metadata so that is_synchronized can access this
    # information.
    mocker.patch(
        "gbif_registrar.utilities.read_local_dataset_metadata",
        return_value=eml,
    )
    mocker.patch(
        "gbif_registrar.utilities.read_gbif_dataset_metadata",
        return_value=gbif_metadata,
    )

    # Check if the dataset is synchronized
    res = is_synchronized(local_dataset_id, file_path=tmp_path / "registrations.csv")
    assert res


def test_is_synchronized_failure(tmp_path, mocker, eml, gbif_metadata):
    """Test that is_synchronized returns False on failure."""
    registrations = read_registrations("tests/registrations.csv")
    registrations.to_csv(tmp_path / "registrations.csv", index=False)
    local_dataset_id = "edi.941.3"
    # Mock the response from read_local_dataset_metadata and
    # read_gbif_dataset_metadata so that is_synchronized can access this
    # information.
    mocker.patch(
        "gbif_registrar.utilities.read_local_dataset_metadata",
        return_value=eml,
    )

    # Case 1: Response from read_gbif_dataset_metadata has the wrong pubDate
    mock_response = gbif_metadata.copy()
    mock_response["pubDate"] = "2019-08-02T00:00:00.000+0000"
    mocker.patch(
        "gbif_registrar.utilities.read_gbif_dataset_metadata",
        return_value=mock_response,
    )
    res = is_synchronized(local_dataset_id, file_path=tmp_path / "registrations.csv")
    assert res is False

    # Case 2: Response from read_gbif_dataset_metadata has the wrong endpoint
    mock_response = gbif_metadata.copy()
    mock_response["endpoints"][0][
        "url"
    ] = "https://pasta-s.lternet.edu/package/data/eml/edi/941/X"
    mocker.patch(
        "gbif_registrar.utilities.read_gbif_dataset_metadata",
        return_value=mock_response,
    )
    res = is_synchronized(local_dataset_id, file_path=tmp_path / "registrations.csv")
    assert res is False
