"""Test utilities"""
import os.path
import hashlib
import pandas as pd
from gbif_registrar.utilities import read_registrations
from gbif_registrar.utilities import initialize_registrations


def test_initialize_registrations_writes_to_path(tmp_path):
    """File is written to path."""
    f = tmp_path / "registrations.csv"
    initialize_registrations(f)
    assert os.path.exists(f)


def test_initialize_registrations_does_not_overwrite(tmp_path):
    """Does not overwrite."""
    f = tmp_path / "registrations.csv"
    initialize_registrations(f)
    with open(f, "rb") as rgstrs:
        md5_before = hashlib.md5(rgstrs.read()).hexdigest()
    with open(f, "rb") as rgstrs:
        md5_after = hashlib.md5(rgstrs.read()).hexdigest()
    assert md5_before == md5_after


def test_initialize_registrations_has_expected_columns(tmp_path):
    """Has expected columns."""
    expected_cols = {
        "local_dataset_id",
        "local_dataset_group_id",
        "local_dataset_endpoint",
        "gbif_dataset_uuid",
        "gbif_crawl_datetime",
    }
    f = tmp_path / "registrations.csv"
    initialize_registrations(f)
    df = pd.read_csv(f, delimiter=",")
    missing_cols = not expected_cols.issubset(set(df.columns))
    assert not missing_cols


def test_read_registrations_reads_file():
    """Reads the file."""
    rgstrs = read_registrations("tests/registrations.csv")
    assert isinstance(rgstrs, pd.DataFrame)


def test_read_registrations_formats_datetime():
    """Formats the datetime column."""
    rgstrs = read_registrations("tests/registrations.csv")
    crawl_time = rgstrs["gbif_crawl_datetime"]
    assert pd.core.dtypes.common.is_datetime64_dtype(crawl_time)
