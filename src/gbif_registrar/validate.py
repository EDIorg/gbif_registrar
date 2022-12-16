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
    """Checks uniqueness of dataset group registrations.

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
    # This can be solved by isolating the 2 columns, dropping replicate rows,
    # and then looking for counts > 1 in the first column (instances of
    # one-to-many relationships), and then doing the same for the other column.
    df = regs[['local_dataset_group_id', 'gbif_dataset_uuid']].drop_duplicates()
    # Check the first column for issues
    group_counts = df['local_dataset_group_id'].value_counts()
    for group_count in list(zip(group_counts.index, group_counts)):
        if group_count[1] > 1:
            warnings.warn('Non-unique group registrations. ' + group_count[0] + ' has > 1 gbif_dataset_uuid.')
    # Then check the second column for issues
    group_counts = df['gbif_dataset_uuid'].value_counts()
    group_counts = list(zip(group_counts.index, group_counts))
    for group_count in group_counts:
        if group_count[1] > 1:
            warnings.warn('Non-unique group registrations. ' + group_count[0] + ' has > 1 local_dataset_group_id.')


def check_local_endpoints(regs):
    """Checks uniqueness of local dataset endpoints

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
    If local_dataset_id and local_dataset_endpoint don't have 1-to-1
        cardinality.

    """
    # Assuming primary keys (local_dataset_id), non-1-to-1 relationships are
    # represented by non-unique endpoints. I.e. only need to look for and report
    # row indices of duplicate local_dataset_endpoint.
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
    check_group_registrations(regs)
    # Local dataset ID and Local dataset endpoint are 1-to-1
    check_local_endpoints(regs)
    # Has been crawled
    if extended_checks:
        pass
    # Local dataset ID has correct format
    # Local dataset ID has correct local dataset group ID