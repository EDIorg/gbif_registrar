"""Test register_dataset.py"""

import os.path
import hashlib
import pandas as pd
from gbif_registrar._utilities import _read_registrations_file, _expected_cols
from gbif_registrar.register import register_dataset
from gbif_registrar.register import initialize_registrations_file
from gbif_registrar.register import complete_registration_records
from gbif_registrar.authenticate import login, logout


def test_complete_registration_records_ignores_complete_registrations(
    tmp_path, registrations
):
    """Test that the complete_registration_records function ignores a complete
    registrations file."""
    # Create a copy of the registrations file for the function to operate on.
    registrations.to_csv(tmp_path / "registrations.csv", index=False)
    complete_registration_records(tmp_path / "registrations.csv")
    registrations_final = _read_registrations_file(tmp_path / "registrations.csv")
    assert registrations_final.shape[0] == registrations.shape[0]
    assert registrations_final.equals(registrations)


def test_complete_registration_records_repairs_failed_registration(
    tmp_path, registrations, mocker, gbif_dataset_uuid
):
    """Test that the complete_registration_records repairs a failed
    registration attempt."""

    login("tests/test_config.json")
    # Mock the response from _get_gbif_dataset_uuid, so we don't have to make
    # an actual HTTP request.
    mocker.patch(
        "gbif_registrar.register._get_gbif_dataset_uuid", return_value=gbif_dataset_uuid
    )

    # Simulate two failed registration attempts and write to file for the
    # function to operate on.
    registrations.iloc[-1, -4:-1] = None
    registrations.iloc[-1, -1] = False
    registrations.iloc[-2, -4:-1] = None
    registrations.iloc[-2, -1] = False
    registrations.to_csv(tmp_path / "registrations.csv", index=False)

    # Run the function and check that the initial and final registrations files
    # have the same shape and that the last row has been repaired.
    complete_registration_records(tmp_path / "registrations.csv")
    registrations_final = _read_registrations_file(tmp_path / "registrations.csv")
    assert registrations_final.shape[0] == registrations.shape[0]
    assert registrations_final.iloc[-1, -4:-1].notnull().all()
    assert registrations_final.iloc[-2, -4:-1].notnull().all()
    logout()


def test_complete_registration_records_operates_on_one_dataset(
    tmp_path, registrations, mocker, gbif_dataset_uuid
):
    """Test that the complete_registration_records function operates on a
    single local_dataset_id when specified."""
    login("tests/test_config.json")
    # Create a registrations file with two incomplete registrations to test
    # that when specified the function only operates on the specified
    # local_dataset_id.
    registrations.iloc[-1, -4:-1] = None  # Make last row incomplete
    registrations.iloc[-1, -1] = False
    registrations.iloc[-2, -4:-1] = None  # Make second to last row incomplete
    registrations.iloc[-2, -1] = False
    registrations.to_csv(tmp_path / "registrations.csv", index=False)
    # Mock the response from _get_gbif_dataset_uuid, so we don't have to make
    # an actual HTTP request.
    mocker.patch(
        "gbif_registrar.register._get_gbif_dataset_uuid", return_value=gbif_dataset_uuid
    )
    # Run the function and check that the initial and final registrations files
    # have the same shape and that the last row has been repaired.
    local_dataset_id = registrations.iloc[-1]["local_dataset_id"]
    complete_registration_records(
        registrations_file=tmp_path / "registrations.csv",
        local_dataset_id=local_dataset_id,
    )
    registrations_final = _read_registrations_file(tmp_path / "registrations.csv")
    assert registrations_final.shape[0] == registrations.shape[0]
    assert registrations_final.iloc[-1, -4:-1].notnull().all()
    assert registrations_final.iloc[-2, -4:-1].isnull().all()
    logout()


def test_complete_registration_records_handles_empty_dataframe(
    tmp_path, registrations, local_dataset_id, mocker, gbif_dataset_uuid
):
    """Test that the complete_registration_records function handles a
    registrations file containing only a local_dataset_id."""
    login("tests/test_config.json")
    # Mock the response from _get_gbif_dataset_uuid, so we don't have to make
    # an actual HTTP request.
    mocker.patch(
        "gbif_registrar.register._get_gbif_dataset_uuid", return_value=gbif_dataset_uuid
    )

    # Create an empty registrations file for the function to operate on.
    registrations = registrations.iloc[0:0]
    registrations = pd.concat(
        [registrations, pd.DataFrame({"local_dataset_id": [local_dataset_id]})]
    )
    registrations["synchronized"] = False
    registrations.to_csv(tmp_path / "registrations.csv", index=False)
    # Run the function and check that the initial and final registrations files
    # have the same shape and that the last row has been repaired.
    complete_registration_records(tmp_path / "registrations.csv")
    registrations_final = _read_registrations_file(tmp_path / "registrations.csv")
    assert registrations_final.shape[0] == registrations.shape[0]
    assert registrations_final.iloc[-1, -4:-1].notnull().all()
    logout()


def test_initialize_registrations_file_does_not_overwrite(tmp_path):
    """Does not overwrite."""
    file = tmp_path / "registrations.csv"
    initialize_registrations_file(file)
    with open(file, "rb") as registrations:
        md5_before = hashlib.md5(registrations.read()).hexdigest()
    with open(file, "rb") as registrations:
        md5_after = hashlib.md5(registrations.read()).hexdigest()
    assert md5_before == md5_after


def test_initialize_registrations_file_has_expected_columns(tmp_path):
    """Has expected columns."""
    file = tmp_path / "registrations.csv"
    initialize_registrations_file(file)
    data = pd.read_csv(file, delimiter=",")
    missing_cols = not set(_expected_cols()).issubset(set(data.columns))
    assert not missing_cols


def test_initialize_registrations_file_writes_to_path(tmp_path):
    """File is written to path."""
    file = tmp_path / "registrations.csv"
    initialize_registrations_file(file)
    assert os.path.exists(file)


def test_read_registrations_reads_file():
    """Reads the file."""
    registrations = _read_registrations_file("tests/registrations.csv")
    assert isinstance(registrations, pd.DataFrame)


def test_read_registrations_casts_dtypes():
    """Test that the _read_registrations_file function casts the columns to
    the expected dtypes."""
    registrations = _read_registrations_file("tests/registrations.csv")
    assert registrations["local_dataset_id"].dtype == "string"
    assert registrations["local_dataset_group_id"].dtype == "string"
    assert registrations["local_dataset_endpoint"].dtype == "string"
    assert registrations["gbif_dataset_uuid"].dtype == "string"
    isinstance(registrations["synchronized"].dtype, pd.BooleanDtype)


def test_register_dataset_success(
    local_dataset_id, gbif_dataset_uuid, tmp_path, registrations, mocker
):
    """Test that the register_dataset function returns a file with a new row
    containing the local_dataset_id along with a gbif_dataset_uuid."""

    login("tests/test_config.json")
    # Create a copy of the registrations file in the temporary test directory
    # so that the test can modify it without affecting the original file.
    registrations.to_csv(tmp_path / "registrations.csv", index=False)

    # Mock the response from _get_gbif_dataset_uuid, so we don't have to make
    # an actual HTTP request.
    mocker.patch(
        "gbif_registrar.register._get_gbif_dataset_uuid", return_value=gbif_dataset_uuid
    )

    # Run the register_dataset function and check that the new row was added
    # to the registrations file, and that the new row contains the local
    # dataset ID and a unique GBIF registration number.
    register_dataset(
        local_dataset_id=local_dataset_id,
        registrations_file=tmp_path / "registrations.csv",
    )
    registrations_final = _read_registrations_file(tmp_path / "registrations.csv")
    assert registrations_final.shape[0] == registrations.shape[0] + 1
    assert registrations_final.iloc[-1]["local_dataset_id"] == local_dataset_id
    assert registrations_final.iloc[-1]["gbif_dataset_uuid"] == gbif_dataset_uuid
    logout()


def test_register_dataset_failure(local_dataset_id, tmp_path, registrations, mocker):
    """Test that the register_dataset function returns a file with a new row
    containing the local_dataset_id, but with the gbif_dataset_uuid value
    set to NA."""

    login("tests/test_config.json")
    # Create a copy of the registrations file in the temporary test directory
    # so that the test can modify it without affecting the original file.
    registrations.to_csv(tmp_path / "registrations.csv", index=False)

    # Mock the response from _get_gbif_dataset_uuid, so we don't have to make
    # an actual HTTP request.
    mocker.patch("gbif_registrar.register._get_gbif_dataset_uuid", return_value=None)

    # Run the register_dataset function and check that the new row was added
    # to the registrations file, and that the new row contains the local
    # dataset ID and no GBIF registration number.
    register_dataset(
        local_dataset_id=local_dataset_id,
        registrations_file=tmp_path / "registrations.csv",
    )
    registrations_final = _read_registrations_file(tmp_path / "registrations.csv")
    assert registrations_final.shape[0] == registrations.shape[0] + 1
    assert registrations_final.iloc[-1]["local_dataset_id"] == local_dataset_id
    assert pd.isna(registrations_final.iloc[-1]["gbif_dataset_uuid"])
    logout()


def test_register_dataset_reuses_uuid_for_updates(tmp_path, registrations):
    """Test that the register_dataset function reuses the gbif_dataset_uuid
    for members of the same local_dataset_group_id. This is necessary for
    updating the metadata and endpoints of a dataset group in GBIF."""
    login("tests/test_config.json")
    # Create a copy of the registrations file in the temporary test directory
    # so that the test can modify it without affecting the original file.
    registrations.to_csv(tmp_path / "registrations.csv", index=False)
    # Register a revision of the dataset group and check that the UUID is
    # the same as the original registration.
    old_local_dataset_id = "edi.941.3"
    old_gbif_dataset_uuid = registrations[
        registrations["local_dataset_id"] == old_local_dataset_id
    ]["gbif_dataset_uuid"]
    new_local_dataset_id = "edi.941.4"
    register_dataset(
        local_dataset_id=new_local_dataset_id,
        registrations_file=tmp_path / "registrations.csv",
    )
    registrations_final = _read_registrations_file(tmp_path / "registrations.csv")
    new_gbif_dataset_uuid = registrations_final[
        registrations_final["local_dataset_id"] == new_local_dataset_id
    ]["gbif_dataset_uuid"]
    assert old_gbif_dataset_uuid.values == new_gbif_dataset_uuid.values
    logout()
