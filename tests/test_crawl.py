"""Test crawl.py"""

import pytest
from gbif_registrar.crawl import upload_dataset
from gbif_registrar.crawl import _post_new_metadata_document


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
