"""A module for validating the registrations file"""

from gbif_registrar.register import _read_registrations_file
from gbif_registrar._utilities import _check_completeness
from gbif_registrar._utilities import _check_local_dataset_id
from gbif_registrar._utilities import _check_group_registrations
from gbif_registrar._utilities import _check_local_endpoints
from gbif_registrar._utilities import _check_synchronized
from gbif_registrar._utilities import _check_local_dataset_id_format
from gbif_registrar._utilities import _check_local_dataset_group_id_format


def validate_registrations(file_path):
    """Validates the registrations file.

    This is a wrapper to `_check_completeness`, `_check_local_dataset_id`,
    `_check_group_registrations`, `_check_local_endpoints`, and
    `_check_synchronized`.

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
    registrations = _read_registrations_file(file_path)
    _check_completeness(registrations)
    _check_local_dataset_id(registrations)
    _check_group_registrations(registrations)
    _check_local_endpoints(registrations)
    _check_synchronized(registrations)
    _check_local_dataset_id_format(registrations)
    _check_local_dataset_group_id_format(registrations)
