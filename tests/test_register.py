"""Test register_dataset.py"""

import os.path
import hashlib
import pandas as pd
from gbif_registrar._utilities import _read_registrations_file, _expected_cols
from gbif_registrar.register import register_dataset
from gbif_registrar.register import initialize_registrations_file
from gbif_registrar.register import complete_registration_records


def test_complete_registration_records_ignores_complete_registrations(tmp_path, rgstrs):
    """Test that the complete_registration_records function ignores a complete
    registrations file."""
    # Create a copy of the registrations file for the function to operate on.
    rgstrs.to_csv(tmp_path / "registrations.csv", index=False)
    complete_registration_records(tmp_path / "registrations.csv")
    rgstrs_final = _read_registrations_file(tmp_path / "registrations.csv")
    assert rgstrs_final.shape[0] == rgstrs.shape[0]
    assert rgstrs_final.equals(rgstrs)


def test_complete_registration_records_repairs_failed_registration(
    tmp_path, rgstrs, mocker, gbif_dataset_uuid
):
    """Test that the complete_registration_records repairs a failed
    registration attempt."""

    # Mock the response from _get_gbif_dataset_uuid, so we don't have to make
    # an actual HTTP request.
    mocker.patch(
        "gbif_registrar.register._get_gbif_dataset_uuid", return_value=gbif_dataset_uuid
    )

    # Simulate a failed registration attempt and write to file for the function
    # to operate on.
    rgstrs.iloc[-1, -4:-1] = None
    rgstrs.iloc[-1, -1] = False
    rgstrs.to_csv(tmp_path / "registrations.csv", index=False)

    # Run the function and check that the initial and final registrations files
    # have the same shape and that the last row has been repaired.
    complete_registration_records(tmp_path / "registrations.csv")
    rgstrs_final = _read_registrations_file(tmp_path / "registrations.csv")
    assert rgstrs_final.shape[0] == rgstrs.shape[0]
    assert rgstrs_final.iloc[-1, -4:-1].notnull().all()


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
    missing_cols = not set(_expected_cols()).issubset(set(data.columns))
    assert not missing_cols


def test_initialize_registrations_file_writes_to_path(tmp_path):
    """File is written to path."""
    file = tmp_path / "registrations.csv"
    initialize_registrations_file(file)
    assert os.path.exists(file)


def test_read_registrations_reads_file():
    """Reads the file."""
    rgstrs = _read_registrations_file("tests/registrations.csv")
    assert isinstance(rgstrs, pd.DataFrame)


def test_read_registrations_casts_dtypes():
    """Test that the _read_registrations_file function casts the columns to
    the expected dtypes."""
    rgstrs = _read_registrations_file("tests/registrations.csv")
    assert rgstrs["local_dataset_id"].dtype == "string"
    assert rgstrs["local_dataset_group_id"].dtype == "string"
    assert rgstrs["local_dataset_endpoint"].dtype == "string"
    assert rgstrs["gbif_dataset_uuid"].dtype == "string"
    isinstance(rgstrs["synchronized"].dtype, pd.BooleanDtype)


def test_register_dataset_success(
    local_dataset_id, gbif_dataset_uuid, tmp_path, rgstrs, mocker
):
    """Test that the register_dataset function returns a file with a new row
    containing the local_dataset_id along with a gbif_dataset_uuid."""

    # Create a copy of the registrations file in the temporary test directory
    # so that the test can modify it without affecting the original file.
    rgstrs.to_csv(tmp_path / "registrations.csv", index=False)

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
    rgstrs_final = _read_registrations_file(tmp_path / "registrations.csv")
    assert rgstrs_final.shape[0] == rgstrs.shape[0] + 1
    assert rgstrs_final.iloc[-1]["local_dataset_id"] == local_dataset_id
    assert rgstrs_final.iloc[-1]["gbif_dataset_uuid"] == gbif_dataset_uuid


def test_register_dataset_failure(local_dataset_id, tmp_path, rgstrs, mocker):
    """Test that the register_dataset function returns a file with a new row
    containing the local_dataset_id, but with the gbif_dataset_uuid value
    set to NA."""

    # Create a copy of the registrations file in the temporary test directory
    # so that the test can modify it without affecting the original file.
    rgstrs.to_csv(tmp_path / "registrations.csv", index=False)

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
    rgstrs_final = _read_registrations_file(tmp_path / "registrations.csv")
    assert rgstrs_final.shape[0] == rgstrs.shape[0] + 1
    assert rgstrs_final.iloc[-1]["local_dataset_id"] == local_dataset_id
    assert pd.isna(rgstrs_final.iloc[-1]["gbif_dataset_uuid"])
