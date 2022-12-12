"""A module for validating the registrations file"""
import pandas as pd


def validate_registrations_file(file_path, extended_checks=False):
    """Checks the registrations file for issues.

    Parameters
    ----------
    file_path : Any
        Path of the registrations file.
    extended_checks : bool
        Run extended checks? Extended checks are repository specific.
        Extended checks are ignored by default. They can be customized by
        editing the source code.

    Returns
    -------
    None

    Warnings
    --------
    Core checks
        If registrations are incomplete.
        If local_dataset_id values (primary keys) are not unique.
        If local_dataset_group_id and gbif_dataset_uuid don't have 1-to-1
        cardinality.
        If local_dataset_id and local_dataset_endpoint don't have 1-to-1
        cardinality.
        If local_dataset_id has not been crawled.
    Extended checks
        If local_dataset_id has an invalid format.
        If local_dataset_id has an incorrect local_dataset_group_id.

    See Also
    --------
    initialize_registrations_file

    Examples
    --------
    >>> validate_registrations('/Users/me/docs/registrations.csv')

    With extended checks

    >>> validate_registrations('/Users/me/docs/registrations.csv', extended_checks=TRUE)
    """
    # read registrations
    # check core criteria
    # check extended
    if extended_checks:
        pass
    return None



def check_core():
    # incomplete registrations
    # unique primary keys
    # Local dataset group ID and GBIF dataset uuid are 1-to-1
    # Local dataset ID and Local dataset endpoint are 1-to-1
    # Has been crawled
    return None

def check_extended():
    # Local dataset ID has correct format
    # Local dataset ID has correct local dataset group ID
    return None

