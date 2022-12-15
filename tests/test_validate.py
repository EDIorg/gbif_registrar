import numpy as np

from gbif_registrar import validate
import warnings
from gbif_registrar import utilities
import pandas as pd


def test_check_completeness_warns_when_incomplete():
    """Incomplete registrations issue warnings."""
    regs = utilities.read_registrations_file("tests/registrations.csv")
    regs.loc[0, 'local_dataset_id'] = np.NaN
    regs.loc[2, 'local_dataset_endpoint'] = np.NaN
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        validate.check_completeness(regs)
        assert "Incomplete registrations" in str(w[0].message)
        assert "1, 3" in str(w[0].message)


def test_check_completeness_does_not_warn_when_complete():
    """Complete registrations don't result in warnings."""
    regs = utilities.read_registrations_file("tests/registrations.csv")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        validate.check_completeness(regs)
        assert len(w) == 0

