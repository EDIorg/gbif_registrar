"""A module for validating the registrations file"""
from src.gbif_registrar.utilities import read_registrations_file
from gbif_registrar.utilities import expected_cols
import warnings


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
        If registrations are incomplete. I.e. is missing any value from a
        dataset registration, except for `gbif_crawl_datetime`, which is not
        essential for initiating a GBIF crawl.
    """
    regs = regs[expected_cols()].drop(['gbif_crawl_datetime'], axis=1)
    regs = regs[regs.isna().any(axis=1)]
    if len(regs) > 0:
        rows = regs.index.to_series() + 1
        rows = rows.astype('string')
        warnings.warn('Incomplete registrations in rows: ' + ', '.join(rows))


def check_local_dataset_id(regs):
    """Check uniqueness of local_dataset_id (primary key)

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
        If values in the `local_dataset_id` column are not unique.
    """
    dupes = regs['local_dataset_id'].duplicated()
    if any(dupes):
        dupes = dupes.index.to_series() + 1
        dupes = dupes.astype('string')
        warnings.warn('Duplicate local_dataset_id values in rows: ' + ', '.join(dupes))


def check_group_registrations(regs):
    """Checks the local_dataset_group_id and gbif_dataset_uuid are 1-to-1.

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
    If local_dataset_group_id and gbif_dataset_uuid don't have 1-to-1
        cardinality.
    """
    pass


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
    regs = read_registrations_file(file_path)
    check_completeness(regs)
    check_local_dataset_id(regs)
    # Local dataset group ID and GBIF dataset uuid are 1-to-1
    check_local_group_and_gbif_id(regs)
    # Local dataset ID and Local dataset endpoint are 1-to-1
    # Has been crawled
    if extended_checks:
        pass
    # Local dataset ID has correct format
    # Local dataset ID has correct local dataset group ID