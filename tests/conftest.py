"""Configure the test suite."""

import pytest
from gbif_registrar.authenticate import login
from gbif_registrar.authenticate import logout
from gbif_registrar._utilities import _read_registrations_file



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


@pytest.fixture(name="gbif_dataset_uuid")
def gbif_dataset_uuid_fixture():
    """Create a gbif_dataset_uuid fixture for tests."""
    # This gbif_dataset_uuid is an example UUID returned by the GBIF API.
    return "4e70c80e-cf22-49a5-8bf7-280994500324"


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


@pytest.fixture(name="local_dataset_endpoint")
def local_dataset_endpoint_fixture():
    """Create a local_dataset_endpoint fixture for tests."""
    # This local_dataset_endpoint corresponds to a data package archived on
    # EDI and formatted according to the DwCA-Event core.
    return "https://pasta.lternet.edu/package/download/eml/edi/929/2"


@pytest.fixture
def local_dataset_group_id():
    """Create a local_dataset_group_id fixture for tests."""
    # This local_dataset_group_id corresponds to a data package archived on
    # EDI and formatted according to the DwCA-Event core. This value is
    # derived from the local_dataset_id fixture and should be the same as the
    # local_dataset_id with the version number removed.
    return "edi.929"


@pytest.fixture(name="local_dataset_id")
def local_dataset_id_fixture():
    """Create a local_dataset_id fixture for tests."""
    # This local_dataset_id corresponds to a data package archived on EDI and
    # formatted according to the DwCA-Event core.
    return "edi.929.2"


@pytest.fixture(name="mock_update_dataset_success")
def mock_update_dataset_success_fixture(mocker, gbif_dataset_uuid):
    """Create a mock_update_dataset_success fixture for tests that use a
    similar pattern of calls to the GBIF API."""
    mocker.patch(
        "gbif_registrar.register._get_gbif_dataset_uuid", return_value=gbif_dataset_uuid
    )
    mocker.patch(
        "gbif_registrar._utilities._delete_local_dataset_endpoints", return_value=None
    )
    mocker.patch(
        "gbif_registrar._utilities._post_local_dataset_endpoint", return_value=None
    )
    mocker.patch(
        "gbif_registrar._utilities._post_new_metadata_document", return_value=None
    )
    # The alternating side effects (below) are required to pass the first
    # synchronization check and continue on to the second synchronization
    # check. We list this pattern twice because update_dataset() is called
    # twice in the test.
    mocker.patch(
        "gbif_registrar._utilities._is_synchronized",
        side_effect=[False, True, False, True],
    )


@pytest.fixture(name="registrations")
def registrations_fixture():
    """Read the test registrations file into DataFrame fixture."""
    return _read_registrations_file("tests/registrations.csv")
