"""Test crawl.py"""

from re import search
import pytest
from gbif_registrar._utilities import (
    _read_registrations_file,
)
from gbif_registrar.register import register_dataset
from gbif_registrar.crawl import upload_dataset


def test_upload_dataset():
    """Test that the upload_dataset function works as expected."""
    # TODO: Mock this test
    # local_dataset_endpoint = "https://pasta-s.lternet.edu/package/download/eml/edi/941/3"
    # local_dataset_id = "edi.941.3"
    # # local_dataset_endpoint = "https://pasta-s.lternet.edu/package/download/eml/edi/941/4"  # Next version
    # # local_dataset_id = "edi.941.4"
    # gbif_dataset_uuid = "cfb3f6d5-ed7d-4fff-9f1b-f032ed1de485"
    # upload_dataset(local_dataset_id, local_dataset_endpoint, gbif_dataset_uuid)
    assert True


# TODO add the capsys fixture to the function signature
def test_upload_dataset_real_requests(rgstrs, tmp_path):
    """Test that the upload_dataset function works as expected using real HTTP
    requests.

    These take a long time to run and may be flaky, but they do provide tests
    of the real system and are therefore valuable. Real tests are done against
    EDI staging and GBIF staging environments."""

    # Set up the test:
    # Copy the registrations file to a temporary directory for modification.
    rgstrs.to_csv(tmp_path / "registrations.csv", index=False)
    # # Remove records for the edi.941 group for reuse in this test.
    # registrations = _read_registrations_file(tmp_path / "registrations.csv")
    # registrations = registrations[registrations["local_dataset_group_id"] != "edi.941"]
    # registrations.to_csv(tmp_path / "registrations.csv", index=False)
    # # Register edi.941.3 with GBIF.
    # local_dataset_id_new = "edi.941.3"
    local_dataset_id_update = "edi.941.4"

    # def test_upload_dataset_new_real_requests(local_dataset_id_new, tmp_path, capsys):
    #     """Test that the upload_dataset function works as expected for a new
    #      dataset upload using real HTTP requests."""
    #     upload_dataset(local_dataset_id_new, tmp_path / "registrations.csv")
    #     assert False
    #     # captured = capsys.readouterr()
    #     # assert "testsss print" in captured.out

    def test_upload_dataset_update_real_requests(local_dataset_id_update, tmp_path):
        """Test that the upload_dataset function works as expected for a
        dataset update using real HTTP requests."""
        # TODO add ', capsys' to the function signature
        register_dataset(local_dataset_id_update, tmp_path / "registrations.csv")
        upload_dataset(local_dataset_id_update, tmp_path / "registrations.csv")
        # captured = capsys.readouterr()
        # assert "dataset group exists on GBIF." in captured.out
        # assert "Deleted existing local dataset endpoints" in captured.out
        # assert "Posted local dataset endpoint" in captured.out
        # assert "Posted new metadata document" in captured.out
        # pattern = "Checking if .+ is synchronized with GBIF."
        # assert search(pattern, captured.out) is not None
        # assert "For more information, see " in captured.out

    # TODO add ', capsys' to the function signature
    test_upload_dataset_update_real_requests(local_dataset_id_update, tmp_path)



    assert False
