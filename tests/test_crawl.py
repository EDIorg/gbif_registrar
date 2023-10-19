"""Test crawl.py"""

from re import search
import pytest
from gbif_registrar._utilities import (
    _read_registrations_file,
)
from gbif_registrar.register import register_dataset
from gbif_registrar.crawl import upload_dataset


def assert_successful_upload(captured, tmp_path, local_dataset_id):
    """Declare test assertions that are shared for both the 'new' and
    'updated' dataset cases, and works for both real and mocked HTTP
    requests."""
    # Check the std out for the expected print statements.
    pattern = "Uploading .+ to GBIF."
    assert search(pattern, captured.out) is not None
    assert "Deleted local dataset endpoints" in captured.out
    assert "Posted local dataset endpoint" in captured.out
    assert "Posted new metadata document" in captured.out
    pattern = "Checking if .+ is synchronized with GBIF."
    assert search(pattern, captured.out) is not None
    pattern = ".+ is synchronized with GBIF."
    assert search(pattern, captured.out) is not None
    assert "Updated the registrations file" in captured.out
    pattern = "Upload of .+ to GBIF is complete."
    assert search(pattern, captured.out) is not None
    assert "View the dataset on GBIF at" in captured.out
    assert "For more information, see " in captured.out
    # Check that the registrations file is updated as expected.
    registrations_final = _read_registrations_file(tmp_path / "registrations.csv")
    assert registrations_final.loc[
        registrations_final["local_dataset_id"] == local_dataset_id, "synchronized"
    ].values[0]


@pytest.mark.skip(reason="Makes real HTTP requests. Run this manually.")
def test_upload_dataset_real_requests(rgstrs, tmp_path, capsys):
    """Test that the upload_dataset function works, for the new and updated
     dataset cases, using real HTTP requests.

    This is an integration test that actually uploads a new dataset, and then
    revised dataset, to the GBIF staging environment from the EDI staging
    environment."""

    # Test the upload of a new dataset ...
    # Remove records for the edi.941 group for reuse in this test
    rgstrs = rgstrs[rgstrs["local_dataset_group_id"] != "edi.941"]
    rgstrs.to_csv(tmp_path / "registrations.csv", index=False)
    # Register edi.941.3 to create a new dataset group on GBIF to upload to.
    local_dataset_id = "edi.941.3"
    register_dataset(local_dataset_id, tmp_path / "registrations.csv")
    # Run the upload_dataset function and assert expected results.
    upload_dataset(local_dataset_id, tmp_path / "registrations.csv")
    captured = capsys.readouterr()
    assert_successful_upload(captured, tmp_path, local_dataset_id)

    # Now, upload an update to the edi.941 group ...
    capsys.readouterr()  # Reset message log for this test
    local_dataset_id = "edi.941.4"
    register_dataset(local_dataset_id, tmp_path / "registrations.csv")
    upload_dataset(local_dataset_id, tmp_path / "registrations.csv")
    captured = capsys.readouterr()
    assert_successful_upload(captured, tmp_path, local_dataset_id)


def test_upload_dataset_mocks(
    rgstrs, tmp_path, capsys, mocker, gbif_dataset_uuid, mock_update_dataset_success
):
    """Test that the upload_dataset function works, for the new and updated
     dataset cases, using mocked HTTP requests.

    This integration test validates the flow control logic of the
    upload_dataset in more detail than test_upload_dataset_real_requests by
    simulating failures and edge cases.
    """

    # Test the upload of a new dataset ...
    # Remove records for the edi.941 group for reuse in this test
    rgstrs = rgstrs[rgstrs["local_dataset_group_id"] != "edi.941"]
    rgstrs.to_csv(tmp_path / "registrations.csv", index=False)
    # Register edi.941.3 to create a new dataset group on GBIF to upload to.
    local_dataset_id = "edi.941.3"
    mocker.patch(
        "gbif_registrar.register._get_gbif_dataset_uuid", return_value=gbif_dataset_uuid
    )
    register_dataset(local_dataset_id, tmp_path / "registrations.csv")
    upload_dataset(local_dataset_id, tmp_path / "registrations.csv")
    captured = capsys.readouterr()
    assert_successful_upload(captured, tmp_path, local_dataset_id)

    # Now, upload an update to the edi.941 group ...
    local_dataset_id = "edi.941.4"
    capsys.readouterr()  # Reset message log for this test
    register_dataset(local_dataset_id, tmp_path / "registrations.csv")
    upload_dataset(local_dataset_id, tmp_path / "registrations.csv")
    captured = capsys.readouterr()
    assert_successful_upload(captured, tmp_path, local_dataset_id)


def test_upload_dataset_missing_local_dataset_id(rgstrs, tmp_path, capsys):
    """Test that the upload_dataset function quits early if the local_dataset_id
    is not in the registrations file."""
    # Remove records for the edi.941 group for reuse in this test
    rgstrs = rgstrs[rgstrs["local_dataset_group_id"] != "edi.941"]
    rgstrs.to_csv(tmp_path / "registrations.csv", index=False)
    # Run the upload_dataset function w/a local_dataset_id that is not in the
    # registrations file.
    local_dataset_id = "edi.941.3"
    upload_dataset(local_dataset_id, tmp_path / "registrations.csv")
    captured = capsys.readouterr()
    assert "is not in the registrations file" in captured.out
    registrations_final = _read_registrations_file(tmp_path / "registrations.csv")
    assert registrations_final.shape == rgstrs.shape
    assert "Deleted local dataset endpoints" not in captured.out  # Never made it here


def test_upload_dataset_already_marked_as_synchronized(rgstrs, tmp_path, capsys):
    """Test that the upload_dataset function quits early if the
    local_dataset_id is marked as synchronized with GBIF. This is the case when
    the function is unnecessarily called."""
    # Set the synchronized column to True for the last row of the
    # registrations, and get the local_dataset_id for use in the test.
    rgstrs.loc[rgstrs.index[-1], "synchronized"] = True
    local_dataset_id = rgstrs.loc[rgstrs.index[-1], "local_dataset_id"]
    rgstrs.to_csv(tmp_path / "registrations.csv", index=False)
    # Run the upload_dataset function
    upload_dataset(local_dataset_id, tmp_path / "registrations.csv")
    captured = capsys.readouterr()
    assert "is already synchronized with GBIF" in captured.out
    registrations_final = _read_registrations_file(tmp_path / "registrations.csv")
    assert registrations_final.shape == rgstrs.shape


def test_upload_dataset_already_synchronized_but_not_listed(
    rgstrs, tmp_path, capsys, mocker
):
    """Test that the upload_dataset function quits early if the
    local_dataset_id is already synchronized with GBIF. This is the case when
    the synchronized column in the registrations file is False because of
    previously timed out synchronization checks."""
    # Set the synchronized column to False for the last row of the
    # registrations, and get the local_dataset_id for use in the test.
    rgstrs.loc[rgstrs.index[-1], "synchronized"] = False
    local_dataset_id = rgstrs.loc[rgstrs.index[-1], "local_dataset_id"]
    rgstrs.to_csv(tmp_path / "registrations.csv", index=False)
    # Mock the synchronization check to return True and run the upload_dataset
    # function.
    mocker.patch("gbif_registrar._utilities._is_synchronized", return_value=True)
    upload_dataset(local_dataset_id, tmp_path / "registrations.csv")
    captured = capsys.readouterr()
    assert (
        "Updated the registrations file with the missing synchronization "
        "status" in captured.out
    )
    registrations_final = _read_registrations_file(tmp_path / "registrations.csv")
    index = registrations_final.index[
        registrations_final["local_dataset_id"] == local_dataset_id
    ].tolist()[0]
    assert registrations_final.loc[index, "synchronized"]
    assert registrations_final.shape == rgstrs.shape
    assert "Deleted local dataset endpoints" not in captured.out  # Never made it here
