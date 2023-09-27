"""Test register_dataset.py"""

import os.path
import hashlib
import pandas as pd
from gbif_registrar.utilities import read_registrations
from gbif_registrar.register import get_local_dataset_group_id
from gbif_registrar.register import get_local_dataset_endpoint
from gbif_registrar.register import get_gbif_dataset_uuid
from gbif_registrar.register import register_dataset
from gbif_registrar.register import request_gbif_dataset_uuid
from gbif_registrar.config import PASTA_ENVIRONMENT
from gbif_registrar.register import initialize_registrations_file
from gbif_registrar.utilities import expected_cols


def test_initialize_registrations_file_writes_to_path(tmp_path):
    """File is written to path."""
    file = tmp_path / "registrations.csv"
    initialize_registrations_file(file)
    assert os.path.exists(file)


def test_initialize_registrations_file_does_not_overwrite(tmp_path):
    """Does not overwrite."""
    file = tmp_path / "registrations.csv"
    initialize_registrations_file(file)
    with open(file, "rb") as rgstrs:
        md5_before = hashlib.md5(rgstrs.read()).hexdigest()
    with open(file, "rb") as rgstrs:
        md5_after = hashlib.md5(rgstrs.read()).hexdigest()
    assert md5_before == md5_after


def test_initialize_registrations_file_has_expected_columns(tmp_path):
    """Has expected columns."""
    file = tmp_path / "registrations.csv"
    initialize_registrations_file(file)
    data = pd.read_csv(file, delimiter=",")
    missing_cols = not set(expected_cols()).issubset(set(data.columns))
    assert not missing_cols


def test_get_local_dataset_group_id(local_dataset_id):
    """Test get_local_dataset_group_id() function.

    The expected value is the local_dataset_id with the version number
    removed."""
    res = get_local_dataset_group_id(local_dataset_id)
    assert res == "edi.929"


def test_get_local_dataset_endpoint(local_dataset_id):
    """Test get_local_dataset_endpoint() function.

    The expected value is a URL composed a base endpoint for the EDI
    repository Download Data Package Archive endpoint and the local dataset ID
    value broken into scope, identifier, and version."""
    res = get_local_dataset_endpoint(local_dataset_id)
    expected = PASTA_ENVIRONMENT + "/package/download/eml/edi/929/2"
    assert res == expected


def test_get_gbif_dataset_uuid_exists(rgstrs):
    """Test that the get_gbif_dataset_uuid function returns the GBIF dataset
    UUID when the local dataset group ID already has a GBIF dataset UUID."""
    row = rgstrs.iloc[-1]
    existing_group_id = row["local_dataset_group_id"]
    existing_uuid = row["gbif_dataset_uuid"]
    res = get_gbif_dataset_uuid(existing_group_id, rgstrs)
    assert res == existing_uuid


def test_get_gbif_dataset_uuid_does_not_exist(rgstrs, mocker):
    """Test that the get_gbif_dataset_uuid function gets a new GBIF dataset
    UUID when the local dataset group ID does not have a GBIF dataset UUID."""
    # Mock the response from get_gbif_dataset_uuid, so we don't have to make
    # an actual HTTP request.
    gbif_dataset_uuid = "a_new_gbif_dataset_uuid"
    mocker.patch(
        "gbif_registrar.register.request_gbif_dataset_uuid",
        return_value=gbif_dataset_uuid,
    )
    # Add new row to the registrations file with a local dataset group ID that
    # does not have a GBIF dataset UUID to trigger the get_gbif_dataset_uuid
    # function to get a new GBIF dataset UUID.
    new_row = rgstrs.iloc[-1].copy()
    new_row["local_dataset_id"] = "edi.929.1"
    new_row["local_dataset_group_id"] = "edi.929"
    new_row[
        "local_dataset_endpoint"
    ] = "https://pasta.lternet.edu/package/download/eml/edi/929/1"
    new_row["gbif_dataset_uuid"] = None
    new_row["is_synchronized"] = False
    rgstrs = rgstrs.append(new_row, ignore_index=True)
    # Run the get_gbif_dataset_uuid function and check that it returns the new
    # GBIF dataset UUID.
    res = get_gbif_dataset_uuid("edi.929", rgstrs)
    assert res == gbif_dataset_uuid


def test_request_gbif_dataset_uuid_success(mocker):
    """Test that the request_gbif_dataset_uuid function returns a UUID string
    when the HTTP request is successful."""
    mock_response = mocker.Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = "4e70c80e-cf22-49a5-8bf7-280994500324"
    mocker.patch("requests.post", return_value=mock_response)
    res = request_gbif_dataset_uuid()
    assert res == "4e70c80e-cf22-49a5-8bf7-280994500324"


def test_request_gbif_dataset_uuid_failure(mocker):
    """Test that the request_gbif_dataset_uuid function returns None when the
    HTTP request fails."""
    mock_response = mocker.Mock()
    mock_response.status_code = 400
    mock_response.reason = "Bad Request"
    mocker.patch("requests.post", return_value=mock_response)
    res = request_gbif_dataset_uuid()
    assert res is None


def test_register_dataset_success(
    local_dataset_id, gbif_dataset_uuid, tmp_path, rgstrs, mocker
):
    """Test that the register_dataset function returns a file with a new row containing
    the local data set ID along with a unique GBIF registration number."""

    # Create a copy of the registrations file in the temporary test directory
    # so that the test can modify it without affecting the original file.
    rgstrs.to_csv(tmp_path / "registrations.csv", index=False)

    # Mock the response from get_gbif_dataset_uuid, so we don't have to make
    # an actual HTTP request.
    mocker.patch(
        "gbif_registrar.register.get_gbif_dataset_uuid", return_value=gbif_dataset_uuid
    )

    # Run the register_dataset function and check that the new row was added to the
    # registrations file, and that the new row contains the local data set ID
    # and a unique GBIF registration number.
    register_dataset(
        local_dataset_id=local_dataset_id,
        registrations_file=tmp_path / "registrations.csv",
    )
    rgstrs_final = read_registrations(tmp_path / "registrations.csv")
    assert rgstrs_final.shape[0] == rgstrs.shape[0] + 1
    assert rgstrs_final.iloc[-1]["local_dataset_id"] == local_dataset_id
    assert rgstrs_final.iloc[-1]["gbif_dataset_uuid"] == gbif_dataset_uuid


def test_register_dataset_repairs_failed_registration(
    local_dataset_id, gbif_dataset_uuid, tmp_path, rgstrs, mocker
):
    """Test that the register_dataset function repairs a failed registration attempt."""

    # Create a copy of the registrations file in the temporary test directory
    # so that the test can modify it without affecting the original file.
    rgstrs.to_csv(tmp_path / "registrations.csv", index=False)

    # Mock the response from get_gbif_dataset_uuid, so we don't have to make
    # an actual HTTP request.
    mocker.patch(
        "gbif_registrar.register.get_gbif_dataset_uuid", return_value=gbif_dataset_uuid
    )

    rgstrs_initial = read_registrations("tests/registrations.csv")
    rgstrs_initial.to_csv(tmp_path / "registrations.csv", index=False)
    register_dataset(
        local_dataset_id=local_dataset_id,
        registrations_file=tmp_path / "registrations.csv",
    )
    rgstrs_initial = read_registrations(tmp_path / "registrations.csv")
    rgstrs_initial.iloc[-1, -4:] = None
    rgstrs_initial.to_csv(tmp_path / "registrations.csv", index=False)
    register_dataset(
        local_dataset_id=local_dataset_id,
        registrations_file=tmp_path / "registrations.csv",
    )
    rgstrs_final = read_registrations(tmp_path / "registrations.csv")
    assert rgstrs_final.shape[0] == rgstrs_initial.shape[0]
    assert rgstrs_final.iloc[-1]["local_dataset_id"] == local_dataset_id
    assert rgstrs_final.iloc[-1]["gbif_dataset_uuid"] == gbif_dataset_uuid
    # The last 3 columns of the last row should not be None. The
    # synchronization status is the only column that should be False because it
    # hasn't been crawled yet.
    assert rgstrs_final.iloc[-1, -4:-1].notnull().all()


def test_register_dataset_ignores_complete_registrations(tmp_path, rgstrs):
    """Test that the register_dataset function ignores complete registrations.

    A new data set is not being registered, and all existing data sets are
    fully registered. The regsitration files should be unchanged."""

    # Create a copy of the registrations file in the temporary test directory
    # so that the test can modify it without affecting the original file.
    rgstrs.to_csv(tmp_path / "registrations.csv", index=False)

    rgstrs_initial = read_registrations("tests/registrations.csv")
    rgstrs_initial.to_csv(tmp_path / "registrations.csv", index=False)
    register_dataset(
        local_dataset_id=None, registrations_file=tmp_path / "registrations.csv"
    )
    rgstrs_final = read_registrations(tmp_path / "registrations.csv")
    assert rgstrs_final.shape[0] == rgstrs_initial.shape[0]
    assert rgstrs_final.equals(rgstrs_initial)
