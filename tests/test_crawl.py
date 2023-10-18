"""Test crawl.py"""

from re import search
import pytest
from gbif_registrar._utilities import (
    _read_registrations_file,
)
from gbif_registrar.register import register_dataset
from gbif_registrar.crawl import upload_dataset


@pytest.mark.skip(reason="Makes real HTTP requests. Run this manually.")
def test_upload_dataset_real_requests(rgstrs, tmp_path, capsys):
    """Test that the upload_dataset function works, for the new and updated
     dataset cases, using real HTTP requests.

    This is an integration test that actually uploads a new dataset, and then
    revised dataset, to the GBIF staging environment from the EDI staging
    environment."""

    def test_assertions(captured):
        """Declare test assertions for both the 'new' and 'updated' dataset
        cases. Results are the same in both cases."""
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
            registrations_final["local_dataset_id"] == "edi.941.3", "synchronized"
        ].values[0]

    # Test the upload of a new dataset ...
    # Remove records for the edi.941 group for reuse in this test
    rgstrs = rgstrs[rgstrs["local_dataset_group_id"] != "edi.941"]
    rgstrs.to_csv(tmp_path / "registrations.csv", index=False)
    # Register edi.941.3 to create a new dataset group on GBIF to upload to.
    register_dataset("edi.941.3", tmp_path / "registrations.csv")
    # Run the upload_dataset function and assert expected results.
    upload_dataset("edi.941.3", tmp_path / "registrations.csv")
    captured = capsys.readouterr()
    test_assertions(captured)

    # Now, upload an update to the edi.941 group ...
    capsys.readouterr()  # Reset message log for this test
    register_dataset("edi.941.4", tmp_path / "registrations.csv")
    upload_dataset("edi.941.4", tmp_path / "registrations.csv")
    captured = capsys.readouterr()
    test_assertions(captured)
