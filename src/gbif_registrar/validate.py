"""Validate the dataset registrations file."""

from gbif_registrar.register import _read_registrations_file
from gbif_registrar._utilities import _check_completeness
from gbif_registrar._utilities import _check_local_dataset_id
from gbif_registrar._utilities import _check_group_registrations
from gbif_registrar._utilities import _check_local_endpoints
from gbif_registrar._utilities import _check_synchronized
from gbif_registrar._utilities import _check_local_dataset_id_format
from gbif_registrar._utilities import _check_local_dataset_group_id_format


def validate_registrations(registrations_file):
    """Validates the dataset registrations file.

    This function validates the dataset registrations file by checking for
    completeness, local dataset ID format, group registrations, local
    endpoints, and synchronization status. If any issues are found, a warning
    is raised.

    Parameters
    ----------
    registrations_file : str or pathlike object
        Path of the dataset registrations file.

    Returns
    -------
    None

    Warns
    -----
    UserWarning
        Warnings are issued if registration issues are found.

    Examples
    --------
    >>> validate_registrations('registrations.csv')
    """
    registrations = _read_registrations_file(registrations_file)
    _check_completeness(registrations)
    _check_local_dataset_id(registrations)
    _check_group_registrations(registrations)
    _check_local_endpoints(registrations)
    _check_synchronized(registrations)
    _check_local_dataset_id_format(registrations)
    _check_local_dataset_group_id_format(registrations)
