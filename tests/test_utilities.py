"""Test utilities"""
import os.path
import hashlib
import pandas as pd
from src.gbif_registrar.utilities import read_registrations_file
from src.gbif_registrar.utilities import initialize_registrations_file


def test_initialize_registrations_file_writes_to_path(tmp_path):
    """File is written to path."""
    f = tmp_path / "registrations.csv"
    initialize_registrations_file(f)
    assert os.path.exists(f)


def test_initialize_registrations_file_does_not_overwrite(tmp_path):
    """Does not overwrite."""
    f = tmp_path / "registrations.csv"
    initialize_registrations_file(f)
    md5 = hashlib.md5(open(f, "rb").read()).hexdigest()
    initialize_registrations_file(f)
    assert md5 == hashlib.md5(open(f, "rb").read()).hexdigest()


def test_initialize_registrations_file_has_expected_columns(tmp_path):
    """Has expected columns."""
    expected_cols = {
        "local_dataset_id",
        "local_dataset_group_id",
        "local_dataset_endpoint",
        "gbif_dataset_uuid",
        "gbif_crawl_datetime",
    }
    f = tmp_path / "registrations.csv"
    initialize_registrations_file(f)
    df = pd.read_csv(f, delimiter=",")
    missing_cols = not expected_cols.issubset(set(df.columns))
    assert not missing_cols


def test_read_registrations_file_reads_file():
    """Reads the file."""
    regs = read_registrations_file("tests/registrations.csv")
    assert isinstance(regs, pd.DataFrame)


def test_read_registrations_file_formats_datetime():
    """Formats the datetime column."""
    regs = read_registrations_file("tests/registrations.csv")
    crawl_time = regs["gbif_crawl_datetime"]
    assert pd.core.dtypes.common.is_datetime64_dtype(crawl_time)
