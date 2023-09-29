"""A module for validating the registrations file"""

from gbif_registrar.register import _read_registrations_file
from gbif_registrar._utilities import (
    _check_completeness,
    _check_local_dataset_id,
    _check_group_registrations,
    _check_local_endpoints,
    _check_is_synchronized,
    _check_local_dataset_id_format,
    _check_local_dataset_group_id_format,
)


def validate_registrations(file_path):
    """Validates the registrations file.

    This is a wrapper to `_check_completeness`, `_check_local_dataset_id`,
    `_check_group_registrations`, `_check_local_endpoints`, and
    `_check_is_synchronized`.

    Parameters
    ----------
    file_path : str or pathlike object
        Path of the registrations file.

    Returns
    -------
    None

    Warns
    -----
    UserWarning
        If registration issues are found.

    Examples
    --------
    >>> validate_registrations('registrations.csv')
    """
    rgstrs = _read_registrations_file(file_path)
    _check_completeness(rgstrs)
    _check_local_dataset_id(rgstrs)
    _check_group_registrations(rgstrs)
    _check_local_endpoints(rgstrs)
    _check_is_synchronized(rgstrs)
    _check_local_dataset_id_format(rgstrs)
    _check_local_dataset_group_id_format(rgstrs)
