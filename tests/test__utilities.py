"""Test utilities"""

from os import environ
import warnings
import numpy as np
import pandas as pd
from gbif_registrar._utilities import (
    _read_local_dataset_metadata,
    _read_gbif_dataset_metadata,
    _is_synchronized,
    _get_local_dataset_group_id,
    _get_local_dataset_endpoint,
    _get_gbif_dataset_uuid,
    _request_gbif_dataset_uuid,
    _check_completeness,
    _check_local_dataset_id,
    _check_one_to_one_cardinality,
    _check_synchronized,
    _check_local_dataset_id_format,
    _check_local_dataset_group_id_format,
    _read_registrations_file,
)
from gbif_registrar.authenticate import login, logout


def test_check_completeness_valid(registrations):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        _check_completeness(registrations)
        assert len(warns) == 0


def test_check_completeness_warns(registrations):
    """An empty value, in a core column, is an incomplete registration."""
    registrations.loc[0, "local_dataset_id"] = np.NaN
    registrations.loc[2, "local_dataset_endpoint"] = np.NaN
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        _check_completeness(registrations)
        assert "Incomplete registrations" in str(warns[0].message)
        assert "1, 3" in str(warns[0].message)


def test_check_local_dataset_id_valid(registrations):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        _check_local_dataset_id(registrations)
        assert len(warns) == 0


def test_check_local_dataset_id_warns(registrations):
    """Non-unique primary keys are an issue, and accompanied by a warning."""
    registrations = pd.concat(
        [registrations, registrations.iloc[[-1]]], ignore_index=True
    )
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        _check_local_dataset_id(registrations)
        assert "Duplicate local_dataset_id values" in str(warns[0].message)
        assert "5" in str(warns[0].message)


def test_check_one_to_one_cardinality_valid(registrations):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        _check_one_to_one_cardinality(
            data=registrations, col1="local_dataset_id", col2="local_dataset_endpoint"
        )
        assert len(warns) == 0


def test_check_one_to_one_cardinality_warn(registrations):
    """Each element in a one-to-one relationship should have only one
    corresponding value, or else a warning is issued."""
    registrations.loc[0, "local_dataset_id"] = registrations.loc[1, "local_dataset_id"]
    registrations.loc[2, "local_dataset_endpoint"] = registrations.loc[
        3, "local_dataset_endpoint"
    ]
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        _check_one_to_one_cardinality(
            data=registrations, col1="local_dataset_id", col2="local_dataset_endpoint"
        )
        assert "should have 1-to-1 cardinality" in str(warns[0].message)
        assert registrations.loc[1, "local_dataset_id"] in str(warns[0].message)
        assert registrations.loc[3, "local_dataset_endpoint"] in str(warns[0].message)


def test_check_is_synchronized_valid(registrations):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        _check_synchronized(registrations)
        assert len(warns) == 0


def test_check_is_synchronized_warn(registrations):
    """Unsynchronized registrations result in a warning."""
    registrations.loc[0, "synchronized"] = False
    registrations.loc[2, "synchronized"] = False
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        _check_synchronized(registrations)
        assert "Unsynchronized registrations in rows" in str(warns[0].message)
        assert "1, 3" in str(warns[0].message)


def test_check_local_dataset_id_format_valid(registrations):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        _check_local_dataset_id_format(registrations)
        assert len(warns) == 0


def test_check_local_dataset_id_format_warn(registrations):
    """Malformed local dataset ID values issue a warning."""
    registrations.loc[0, "local_dataset_id"] = "edi"
    registrations.loc[2, "local_dataset_id"] = "knb-lter-msp.1"
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        _check_local_dataset_id_format(registrations)
        assert "Invalid local_dataset_id values in rows" in str(warns[0].message)
        assert "1, 3" in str(warns[0].message)


def test_check_local_dataset_group_id_format_valid(registrations):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        _check_local_dataset_group_id_format(registrations)
        assert len(warns) == 0


def test_check_local_dataset_group_id_format_warn(registrations):
    """Malformed local dataset group ID values issue a warning."""
    registrations.loc[0, "local_dataset_group_id"] = "edi.xxx"
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        _check_local_dataset_group_id_format(registrations)
        assert "Invalid local_dataset_group_id values in rows" in str(warns[0].message)
        assert "1" in str(warns[0].message)


def test_is_synchronized_success(tmp_path, mocker, eml, gbif_metadata):
    """Test that _is_synchronized returns True on success."""
    login("tests/test_config.json")
    registrations = _read_registrations_file("tests/registrations.csv")
    # Add new line to registrations with a dataset that is synchronized with
    # GBIF so that _is_synchronized can access this information via the
    # registrations_file argument.

    local_dataset_id = "edi.941.3"
    new_row = {
        "local_dataset_id": local_dataset_id,
        "local_dataset_group_id": "edi.941",
        "gbif_dataset_uuid": "cfb3f6d5-ed7d-4fff-9f1b-f032ed1de485",
        "local_dataset_endpoint": "https://pasta-s.lternet.edu/package/data/eml/edi/941/3",
        "is_synchronized": True,
    }
    registrations = pd.concat(
        objs=[registrations, pd.DataFrame(new_row, index=[0])], ignore_index=True
    )
    registrations.to_csv(tmp_path / "registrations.csv", index=False)

    # Mock the response from _read_local_dataset_metadata and
    # _read_gbif_dataset_metadata so that _is_synchronized can access this
    # information.
    mocker.patch(
        "gbif_registrar._utilities._read_local_dataset_metadata",
        return_value=eml,
    )
    mocker.patch(
        "gbif_registrar._utilities._read_gbif_dataset_metadata",
        return_value=gbif_metadata,
    )

    # Check if the dataset is synchronized
    res = _is_synchronized(local_dataset_id, file_path=tmp_path / "registrations.csv")
    assert res
    logout()


def test_is_synchronized_failure(tmp_path, mocker, eml, gbif_metadata):
    """Test that _is_synchronized returns False on failure."""
    login("tests/test_config.json")
    registrations = _read_registrations_file("tests/registrations.csv")
    registrations.to_csv(tmp_path / "registrations.csv", index=False)
    local_dataset_id = "edi.941.3"
    # Mock the response from _read_local_dataset_metadata and
    # _read_gbif_dataset_metadata so that _is_synchronized can access this
    # information.
    mocker.patch(
        "gbif_registrar._utilities._read_local_dataset_metadata",
        return_value=eml,
    )

    # Case 1: Response from _read_gbif_dataset_metadata has the wrong pubDate
    mock_response = gbif_metadata.copy()
    mock_response["pubDate"] = "2019-08-02T00:00:00.000+0000"
    mocker.patch(
        "gbif_registrar._utilities._read_gbif_dataset_metadata",
        return_value=mock_response,
    )
    res = _is_synchronized(local_dataset_id, file_path=tmp_path / "registrations.csv")
    assert res is False

    # Case 2: Response from _read_gbif_dataset_metadata has the wrong endpoint
    mock_response = gbif_metadata.copy()
    mock_response["endpoints"][0][
        "url"
    ] = "https://pasta-s.lternet.edu/package/data/eml/edi/941/X"
    mocker.patch(
        "gbif_registrar._utilities._read_gbif_dataset_metadata",
        return_value=mock_response,
    )
    res = _is_synchronized(local_dataset_id, file_path=tmp_path / "registrations.csv")
    assert res is False
    logout()


def test_get_local_dataset_group_id(local_dataset_id):
    """Test _get_local_dataset_group_id() function.

    The expected value is the local_dataset_id with the version number
    removed."""
    res = _get_local_dataset_group_id(local_dataset_id)
    assert res == "edi.929"


def test_get_local_dataset_endpoint(local_dataset_id):
    """Test _get_local_dataset_endpoint() function.

    The expected value is a URL composed a base endpoint for the EDI
    repository Download Data Package Archive endpoint and the local dataset ID
    value broken into scope, identifier, and version."""
    login("tests/test_config.json")
    res = _get_local_dataset_endpoint(local_dataset_id)
    expected = environ["PASTA_ENVIRONMENT"] + "/package/download/eml/edi/929/2"
    assert res == expected
    logout()


def test_get_gbif_dataset_uuid_exists(registrations):
    """Test that the _get_gbif_dataset_uuid function returns the GBIF dataset
    UUID when the local dataset group ID already has a GBIF dataset UUID."""
    row = registrations.iloc[-1]
    existing_group_id = row["local_dataset_group_id"]
    existing_uuid = row["gbif_dataset_uuid"]
    res = _get_gbif_dataset_uuid(existing_group_id, registrations)
    assert res == existing_uuid


def test_get_gbif_dataset_uuid_does_not_exist(registrations, mocker):
    """Test that the _get_gbif_dataset_uuid function gets a new GBIF dataset
    UUID when the local dataset group ID does not have a GBIF dataset UUID."""
    # Mock the response from _get_gbif_dataset_uuid, so we don't have to make
    # an actual HTTP request.
    gbif_dataset_uuid = "a_new_gbif_dataset_uuid"
    mocker.patch(
        "gbif_registrar._utilities._request_gbif_dataset_uuid",
        return_value=gbif_dataset_uuid,
    )
    # Add new row to the registrations file with a local dataset group ID that
    # does not have a GBIF dataset UUID to trigger the _get_gbif_dataset_uuid
    # function to get a new GBIF dataset UUID.
    new_row = pd.DataFrame(
        {
            "local_dataset_id": "edi.929.1",
            "local_dataset_group_id": "edi.929",
            "local_dataset_endpoint": "https://pasta.lternet.edu/package/download/eml/edi/929/1",
            "is_synchronized": False,
        },
        index=[0],
    )
    registrations = pd.concat(objs=[registrations, new_row], ignore_index=True)
    # Run the _get_gbif_dataset_uuid function and check that it returns the new
    # GBIF dataset UUID.
    res = _get_gbif_dataset_uuid("edi.929", registrations)
    assert res == gbif_dataset_uuid


def test_read_local_dataset_metadata_success(mocker, eml):
    """Test that _read_local_dataset_metadata returns a string on success."""
    login("tests/test_config.json")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = eml
    mocker.patch("requests.get", return_value=mock_response)
    metadata = _read_local_dataset_metadata("knb-lter-ble.20.1")
    assert isinstance(metadata, str)
    logout()


def test_read_local_dataset_metadata_failure(mocker):
    """Test that _read_local_dataset_metadata returns None on failure."""
    login("tests/test_config.json")
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.reason = "Not Found"
    mocker.patch("requests.get", return_value=mock_response)
    metadata = _read_local_dataset_metadata("knb-lter-ble.20.10")
    assert metadata is None
    logout()


def test_read_gbif_dataset_metadata_success(mocker):
    """Test that _read_gbif_dataset_metadata returns a dict on success."""
    login("tests/test_config.json")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = """{"title":"This is a title"}"""
    mocker.patch("requests.get", return_value=mock_response)
    res = _read_gbif_dataset_metadata("cfb3f6d5-ed7d-4fff-9f1b-f032ed1de485")
    assert isinstance(res, dict)
    logout()


def test_read_gbif_dataset_metadata_failure(mocker):
    """Test that _read_gbif_dataset_metadata returns None on failure."""
    login("tests/test_config.json")
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.reason = "Not Found"
    mocker.patch("requests.get", return_value=mock_response)
    res = _read_gbif_dataset_metadata("cfb3f6d5-ed7d-4fff-9f1b-f032e")
    assert res is None
    logout()


def test_request_gbif_dataset_uuid_success(mocker):
    """Test that the _request_gbif_dataset_uuid function returns a UUID string
    when the HTTP request is successful."""
    login("tests/test_config.json")
    mock_response = mocker.Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = "4e70c80e-cf22-49a5-8bf7-280994500324"
    mocker.patch("requests.post", return_value=mock_response)
    res = _request_gbif_dataset_uuid()
    assert res == "4e70c80e-cf22-49a5-8bf7-280994500324"
    logout()


def test_request_gbif_dataset_uuid_failure(mocker):
    """Test that the _request_gbif_dataset_uuid function returns None when the
    HTTP request fails."""
    login("tests/test_config.json")
    mock_response = mocker.Mock()
    mock_response.status_code = 400
    mock_response.reason = "Bad Request"
    mocker.patch("requests.post", return_value=mock_response)
    res = _request_gbif_dataset_uuid()
    assert res is None
    logout()
