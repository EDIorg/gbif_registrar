"""Test utilities"""
import os.path
import hashlib
import pandas as pd
from gbif_registrar.utilities import read_registrations
from gbif_registrar.utilities import initialize_registrations
from gbif_registrar.utilities import expected_cols
from gbif_registrar.utilities import read_local_dataset_metadata
from gbif_registrar.utilities import has_metadata


def test_initialize_registrations_writes_to_path(tmp_path):
    """File is written to path."""
    file = tmp_path / "registrations.csv"
    initialize_registrations(file)
    assert os.path.exists(file)


def test_initialize_registrations_does_not_overwrite(tmp_path):
    """Does not overwrite."""
    file = tmp_path / "registrations.csv"
    initialize_registrations(file)
    with open(file, "rb") as rgstrs:
        md5_before = hashlib.md5(rgstrs.read()).hexdigest()
    with open(file, "rb") as rgstrs:
        md5_after = hashlib.md5(rgstrs.read()).hexdigest()
    assert md5_before == md5_after


def test_initialize_registrations_has_expected_columns(tmp_path):
    """Has expected columns."""
    file = tmp_path / "registrations.csv"
    initialize_registrations(file)
    data = pd.read_csv(file, delimiter=",")
    missing_cols = not set(expected_cols()).issubset(set(data.columns))
    assert not missing_cols


def test_read_registrations_reads_file():
    """Reads the file."""
    rgstrs = read_registrations("tests/registrations.csv")
    assert isinstance(rgstrs, pd.DataFrame)


def test_read_registrations_formats_datetime():
    """Formats the datetime column."""
    rgstrs = read_registrations("tests/registrations.csv")
    crawl_time = rgstrs["gbif_endpoint_set_datetime"]
    assert pd.core.dtypes.common.is_datetime64_dtype(crawl_time)


def test_read_local_dataset_metadata_returns_str():
    """Test that read_local_dataset_metadata returns a string."""
    metadata = read_local_dataset_metadata("edi.941.3")
    assert isinstance(metadata, str)


def test_has_metadata_returns_expected_type():
    """Test that the has_metadata function returns a boolean."""
    res = has_metadata("cfb3f6d5-ed7d-4fff-9f1b-f032ed1de485")
    assert isinstance(res, bool)
