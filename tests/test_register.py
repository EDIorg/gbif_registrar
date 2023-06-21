"""Test register.py"""
import pytest
from gbif_registrar.utilities import read_registrations
from gbif_registrar.register import get_local_dataset_group_id
from gbif_registrar.register import get_local_dataset_endpoint
from gbif_registrar.register import get_gbif_dataset_uuid
from gbif_registrar.register import register


@pytest.fixture
def rgstrs():
    """Read the test registrations file into DataFrame fixture."""
    rgstrs = read_registrations("tests/registrations.csv")
    return rgstrs


@pytest.fixture
def local_dataset_id():
    """Create a local_dataset_id fixture for tests."""
    # This local_dataset_id corresponds to a data package archived on EDI and
    # formatted according to the DwCA-Event core.
    local_dataset_id = "edi.929.2"
    return local_dataset_id


@pytest.fixture
def local_dataset_group_id():
    """Create a local_dataset_group_id fixture for tests."""
    # This local_dataset_group_id corresponds to a data package archived on
    # EDI and formatted according to the DwCA-Event core. This value is
    # derived from the local_dataset_id fixture and should be the same as the
    # local_dataset_id with the version number removed.
    local_dataset_group_id = "edi.929"
    return local_dataset_group_id


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
    expected = "https://pasta.lternet.edu/package/docs/api#GET%20:%20/" + \
               "download/eml/" + \
               "edi/929/2"
    assert res == expected


def test_get_gbif_dataset_uuid(local_dataset_id, local_dataset_group_id,
                               rgstrs):
    """Test get_gbif_dataset_uuid() function.

    The expected value is a UUID string, which is returned in both cases on
    which this function operates: 1. The local dataset group ID already has
    a GBIF dataset UUID; 2. The local dataset group ID does not have a GBIF
    dataset UUID."""

    # Test case 1: local dataset group ID already has a GBIF dataset UUID.
    row = rgstrs.iloc[-1]
    existing_group_id = row["local_dataset_group_id"]
    existing_uuid = row["gbif_dataset_uuid"]
    res = get_gbif_dataset_uuid(existing_group_id, rgstrs)
    assert res == existing_uuid

    # Test case 2: local dataset group ID does not have a GBIF dataset UUID.
    # TODO: Stub out the GBIF API call to test this case.
    # res = get_gbif_dataset_uuid(local_dataset_group_id, rgstrs)


def test_request_gbif_dataset_uuid(local_dataset_id):
    """Test request_gbif_dataset_uuid() function.

    The expected value is a UUID string on success or None in the case of a
    failed HTTP request."""
    # Case 1: UUID is returned.
    # res = request_gbif_dataset_uuid(local_dataset_id)
    # Case 2: HTTP request fails.
    # TODO: Stub out the GBIF API call to test this case.
    assert True


def test_register(local_dataset_id, tmp_path):
    """Test register() function.

    This function has three behaviors: 1. A new data set is being registered
    for the first time; 2. A new data set failed during a previous registration
    attempt and the function is being run again to fix this; 3. A new data set
    is not being registered, and all existing data sets are fully registered,
    which represents a case in which the user ran the function for some "other"
     reason."""
    # Create a copy of the registrations file in the temporary test directory
    # so that the test can modify it without affecting the original file.
    rgstrs_initial = read_registrations("tests/registrations.csv")
    rgstrs_initial.to_csv(tmp_path / "registrations.csv", index=False)

    # Case 1: A new data set is being registered for the first time. The
    # resultant registrations file should have a new row containing the local
    # data set ID along with a unique GBIF registration number.
    register(
        file_path=tmp_path / "registrations.csv",
        local_dataset_id=local_dataset_id
    )
    rgstrs_final = read_registrations(tmp_path / "registrations.csv")
    assert rgstrs_final.shape[0] == rgstrs_initial.shape[0] + 1
    assert rgstrs_final.iloc[-1]["local_dataset_id"] == local_dataset_id
    assert rgstrs_final.iloc[-1]["gbif_dataset_uuid"] not in set(rgstrs_initial["gbif_dataset_uuid"])

    # Case 2: A new data set failed during a previous registration attempt and
    # the function is being run again to fix this.
    rgstrs_initial = read_registrations("tests/registrations.csv")
    rgstrs_initial.to_csv(tmp_path / "registrations.csv", index=False)
    register(
        file_path=tmp_path / "registrations.csv",
        local_dataset_id=local_dataset_id
    )
    rgstrs_initial = read_registrations(tmp_path / "registrations.csv")
    rgstrs_initial.iloc[-1, -4:] = None
    rgstrs_initial.to_csv(tmp_path / "registrations.csv", index=False)
    register(
        file_path=tmp_path / "registrations.csv",
        local_dataset_id=local_dataset_id
    )
    rgstrs_final = read_registrations(tmp_path / "registrations.csv")
    assert rgstrs_final.shape[0] == rgstrs_initial.shape[0]
    assert rgstrs_final.iloc[-1]["local_dataset_id"] == local_dataset_id
    assert rgstrs_final.iloc[-1]["gbif_dataset_uuid"] not in set(
        rgstrs_initial["gbif_dataset_uuid"])
    # The last 3 columns of the last row should not be None. The datetime is
    # the only column that should be None because it hasn't been crawled yet.
    assert rgstrs_final.iloc[-2, -4:].notnull().all()

    # Case 3: A new data set is not being registered, and all existing data
    # sets are fully registered. The regsitration files should be unchanged.
    rgstrs_initial = read_registrations("tests/registrations.csv")
    rgstrs_initial.to_csv(tmp_path / "registrations.csv", index=False)
    register(
        file_path=tmp_path / "registrations.csv"
    )
    rgstrs_final = read_registrations(tmp_path / "registrations.csv")
    assert rgstrs_final.shape[0] == rgstrs_initial.shape[0]
    assert rgstrs_final.equals(rgstrs_initial)

