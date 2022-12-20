import numpy as np
import pytest
from gbif_registrar import validate
import warnings
from gbif_registrar import utilities
import pandas as pd


@pytest.fixture
def regs():
    regs = utilities.read_registrations_file('tests/registrations.csv')
    return regs


def test_check_completeness_valid(regs):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        validate.check_completeness(regs)
        assert len(w) == 0


def test_check_completeness_warns(regs):
    """An empty value, in a core column, is an incomplete registration."""
    regs.loc[0, 'local_dataset_id'] = np.NaN
    regs.loc[2, 'local_dataset_endpoint'] = np.NaN
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        validate.check_completeness(regs)
        assert 'Incomplete registrations' in str(w[0].message)
        assert '1, 3' in str(w[0].message)


def test_check_local_dataset_id_valid(regs):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        validate.check_local_dataset_id(regs)
        assert len(w) == 0


def test_check_local_dataset_id_warns(regs):
    """Non-unique primary keys are an issue, and accompanied by a warning."""
    regs = pd.concat([regs, regs.iloc[[-1]]], ignore_index=True)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        validate.check_local_dataset_id(regs)
        assert 'Duplicate local_dataset_id values' in str(w[0].message)
        assert '5' in str(w[0].message)


def test_check_one_to_one_cardinality_valid(regs):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        validate.check_one_to_one_cardinality(df=regs, col1='local_dataset_id', col2='local_dataset_endpoint')
        assert len(w) == 0


def test_check_one_to_one_cardinality_warn(regs):
    """Each element in a one-to-one relationship should have only one
    corresponding value, or else a warning is issued."""
    regs.loc[0, 'local_dataset_id'] = regs.loc[1, 'local_dataset_id']
    regs.loc[2, 'local_dataset_endpoint'] = regs.loc[
        3, 'local_dataset_endpoint']
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        validate.check_one_to_one_cardinality(df=regs, col1='local_dataset_id', col2='local_dataset_endpoint')
        assert 'should have 1-to-1 cardinality' in str(w[0].message)
        assert regs.loc[1, 'local_dataset_id'] in str(w[0].message)
        assert regs.loc[3, 'local_dataset_endpoint'] in str(w[0].message)


def test_check_crawl_datetime_valid(regs):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        validate.check_crawl_datetime(regs)
        assert len(w) == 0


def test_check_crawl_datetime_warn(regs):
    """Uncrawled registrations result in a warning."""
    regs.loc[0, 'gbif_crawl_datetime'] = np.nan
    regs.loc[2, 'gbif_crawl_datetime'] = np.nan
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        validate.check_crawl_datetime(regs)
        assert 'Uncrawled registrations in rows' in str(w[0].message)
        assert '1, 3' in str(w[0].message)
