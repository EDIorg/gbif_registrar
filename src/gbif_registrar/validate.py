"""A module for validating the registrations file"""
from src.gbif_registrar.utilities import read_registrations_file
import warnings


def validate_registrations_file(file_path, extended_checks=False):
    """Checks the registrations file for issues.

    Parameters
    ----------
    file_path : str or pathlike object
        Path of the registrations file.
    extended_checks : bool
        Run extended checks? Extended checks are repository specific.
        Extended checks are ignored by default. They can be customized by
        editing the source code.

    Returns
    -------
    None

    Warns
    -----
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
    registrations = read_registrations_file(file_path)
    check_core(registrations)
    if extended_checks:
        check_extended(registrations)
    return None


def check_core(regs):
    """Checks registrations for core properties.

    Parameters
    ----------
    regs : pandas.DataFrame
        Create this with `read_registrations_file`.

    Returns
    -------
    None
    """
    check_completeness(regs)
    # unique primary keys
    # Local dataset group ID and GBIF dataset uuid are 1-to-1
    # Local dataset ID and Local dataset endpoint are 1-to-1
    # Has been crawled
    return None


def check_completeness(regs):
    """Checks for registration completeness.

    Parameters
    ----------
    regs : pandas.DataFrame
        A dataframe of the registrations file. Use`read_registrations_file` to
        create this.

    Returns
    -------
    None

    Warns
    -----
    UserWarning
        If registrations are incomplete. I.e. Is missing any value from a
        dataset registration, except for `gbif_crawl_datetime`, which is not
        essential for initiating a GBIF crawl.
    """
    regs
    warnings.warn('Incomplete registrations')


def check_extended(regs):
    """

    Parameters
    ----------
    regs : DataFrame
        A Pandas DataFrame of the registrations file.  Use
        `read_registrations_file` to create this.

    Returns
    -------
    None


    Examples
    --------
    >>> regs = read_registrations_file('/Users/me/docs/registrations.csv')
    >>> check_core(regs)
    """

    # Local dataset ID has correct format
    # Local dataset ID has correct local dataset group ID
    return None

