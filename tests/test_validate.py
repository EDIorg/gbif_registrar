"""Test validate"""

import warnings
import numpy as np
import pandas as pd
from gbif_registrar import validate


def test_check_completeness_valid(rgstrs):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        validate.check_completeness(rgstrs)
        assert len(warns) == 0


def test_check_completeness_warns(rgstrs):
    """An empty value, in a core column, is an incomplete registration."""
    rgstrs.loc[0, "local_dataset_id"] = np.NaN
    rgstrs.loc[2, "local_dataset_endpoint"] = np.NaN
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        validate.check_completeness(rgstrs)
        assert "Incomplete registrations" in str(warns[0].message)
        assert "1, 3" in str(warns[0].message)


def test_check_local_dataset_id_valid(rgstrs):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        validate.check_local_dataset_id(rgstrs)
        assert len(warns) == 0


def test_check_local_dataset_id_warns(rgstrs):
    """Non-unique primary keys are an issue, and accompanied by a warning."""
    rgstrs = pd.concat([rgstrs, rgstrs.iloc[[-1]]], ignore_index=True)
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        validate.check_local_dataset_id(rgstrs)
        assert "Duplicate local_dataset_id values" in str(warns[0].message)
        assert "5" in str(warns[0].message)


def test_check_one_to_one_cardinality_valid(rgstrs):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        validate.check_one_to_one_cardinality(
            data=rgstrs, col1="local_dataset_id", col2="local_dataset_endpoint"
        )
        assert len(warns) == 0


def test_check_one_to_one_cardinality_warn(rgstrs):
    """Each element in a one-to-one relationship should have only one
    corresponding value, or else a warning is issued."""
    rgstrs.loc[0, "local_dataset_id"] = rgstrs.loc[1, "local_dataset_id"]
    rgstrs.loc[2, "local_dataset_endpoint"] = rgstrs.loc[3, "local_dataset_endpoint"]
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        validate.check_one_to_one_cardinality(
            data=rgstrs, col1="local_dataset_id", col2="local_dataset_endpoint"
        )
        assert "should have 1-to-1 cardinality" in str(warns[0].message)
        assert rgstrs.loc[1, "local_dataset_id"] in str(warns[0].message)
        assert rgstrs.loc[3, "local_dataset_endpoint"] in str(warns[0].message)


def test_check_crawl_datetime_valid(rgstrs):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        validate.check_crawl_datetime(rgstrs)
        assert len(warns) == 0


def test_check_crawl_datetime_warn(rgstrs):
    """Uncrawled registrations result in a warning."""
    rgstrs.loc[0, "gbif_endpoint_set_datetime"] = np.nan
    rgstrs.loc[2, "gbif_endpoint_set_datetime"] = np.nan
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        validate.check_crawl_datetime(rgstrs)
        assert "Uncrawled registrations in rows" in str(warns[0].message)
        assert "1, 3" in str(warns[0].message)


def test_check_local_dataset_id_format_valid(rgstrs):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        validate.check_local_dataset_id_format(rgstrs)
        assert len(warns) == 0


def test_check_local_dataset_id_format_warn(rgstrs):
    """Malformed local dataset ID values issue a warning."""
    rgstrs.loc[0, "local_dataset_id"] = "edi"
    rgstrs.loc[2, "local_dataset_id"] = "knb-lter-msp.1"
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        validate.check_local_dataset_id_format(rgstrs)
        assert "Invalid local_dataset_id values in rows" in str(warns[0].message)
        assert "1, 3" in str(warns[0].message)


def test_check_local_dataset_group_id_format_valid(rgstrs):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        validate.check_local_dataset_group_id_format(rgstrs)
        assert len(warns) == 0


def test_check_local_dataset_group_id_format_warn(rgstrs):
    """Malformed local dataset group ID values issue a warning."""
    rgstrs.loc[0, "local_dataset_group_id"] = "edi.xxx"
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter("always")
        validate.check_local_dataset_group_id_format(rgstrs)
        assert "Invalid local_dataset_group_id values in rows" in str(warns[0].message)
        assert "1" in str(warns[0].message)
