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


def test_check_group_registrations_valid(regs):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        validate.check_group_registrations(regs)
        assert len(w) == 0


def test_check_group_registrations_warn(regs):
    """Each local_dataset_group_id should have only one gbif_dataset_group_id
    (and vise versa) or else a warning is issued."""
    regs.loc[0, 'local_dataset_group_id'] = 'bad_id'
    regs.loc[2, 'gbif_dataset_uuid'] = 'bad_id'
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        validate.check_group_registrations(regs)
        assert 'Non-unique group registrations' in str(w[0].message)
        assert 'edi.356' in str(w[0].message)
        assert 'Non-unique group registrations' in str(w[1].message)
        assert 'e44c5367-9d09-4328-9a5a-d0f41fb22d61' in str(w[1].message)


def test_check_local_endpoints_valid(regs):
    """The registrations file is valid, and doesn't throw a warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        validate.check_local_endpoints(regs)
        assert len(w) == 0


def test_check_local_endpoints_warn(regs): # FIXME refactor this
    """Each local_dataset_id should have only one local_dataset_endpoint
    (and vise versa) or else a warning is issued."""
    regs.loc[0, 'local_dataset_id'] = 'bad_id'
    regs.loc[2, 'local_dataset_endpoint'] = 'bad_endpoint' # FIXME duplicate existing endpoint
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        validate.check_local_endpoints(regs)
        assert 'Non-unique dataset endpoints' in str(w[0].message)
        assert 'edi.356' in str(w[0].message)
        assert 'Non-unique dataset endpoints' in str(w[1].message)
        assert 'https://pasta.lternet.edu/package/archive/eml/edi/356/1/archive_edi.356.1_74665239205233345' in str(w[1].message)
