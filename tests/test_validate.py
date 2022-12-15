import numpy as np

from gbif_registrar import validate
import warnings
from gbif_registrar import utilities
import pandas as pd


def test_check_completeness():
    """Incomplete registrations issue warnings."""
    regs = utilities.read_registrations_file("tests/registrations.csv")
    regs.loc[0, 'local_dataset_id'] = np.NaN
    regs.loc[1, 'local_dataset_group_id'] = np.NaN
    regs.loc[2, 'local_dataset_endpoint'] = np.NaN
    regs.loc[3, 'gbif_dataset_uuid'] = np.NaN
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        validate.check_completeness(regs)
        assert "Incomplete registrations" in str(w[0].message)

