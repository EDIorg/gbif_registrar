"""Test utilities"""

from json import loads
import pandas as pd
from gbif_registrar.utilities import read_registrations_file
from gbif_registrar.utilities import read_local_dataset_metadata
from gbif_registrar.utilities import has_metadata
from gbif_registrar.utilities import read_gbif_dataset_metadata
from gbif_registrar.utilities import is_synchronized


def test_read_registrations_reads_file():
    """Reads the file."""
    rgstrs = read_registrations_file("tests/registrations.csv")
    assert isinstance(rgstrs, pd.DataFrame)


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
    registrations = read_registrations_file("tests/registrations.csv")
    # Add new line to registrations with a dataset that is synchronized with
    # GBIF so that is_synchronized can access this information via the
    # registrations_file argument.
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
    registrations = read_registrations_file("tests/registrations.csv")
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
