"""A module for validating the registrations file"""
from src.gbif_registrar.utilities import read_registrations_file
from gbif_registrar.utilities import expected_cols
import warnings
import pandas as pd


def check_completeness(regs):
    """Checks registrations for completeness.

    A complete registration has values for all fields except (perhaps)
    `gbif_crawl_datetime`, which is not essential for initiating a GBIF
    crawl.

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
        If any registrations are incomplete.

    Examples
    --------
    >>> regs = read_registrations_file('tests/registrations.csv')
    >>> check_completeness(regs)
    """
    regs = regs[expected_cols()].drop(['gbif_crawl_datetime'], axis=1)
    regs = regs[regs.isna().any(axis=1)]
    if len(regs) > 0:
        rows = regs.index.to_series() + 1
        rows = rows.astype('string')
        warnings.warn('Incomplete registrations in rows: ' + ', '.join(rows))


def check_local_dataset_id(regs):
    """Checks registrations for unique local_dataset_id.

    Each registration is represented by a unique primary key, i.e. the
    `local_dataset_id`.

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

    Examples
    --------
    >>> regs = read_registrations_file('tests/registrations.csv')
    >>> check_local_dataset_id(regs)
    """
    dupes = regs['local_dataset_id'].duplicated()
    if any(dupes):
        dupes = dupes.index.to_series() + 1
        dupes = dupes.astype('string')
        warnings.warn('Duplicate local_dataset_id values in rows: ' + ', '.join(dupes))


def check_one_to_one_cardinality(df, col1, col2):
    """Check for one-to-one cardinality between two columns of a dataframe.

    This is a helper function used in a couple registration checks.

    Parameters
    ----------
    df : pandas.DataFrame
    col1 : str
        Column name
    col2 : str
        Column name

    Returns
    -------
    None

    Warns
    -----
    If `col1` and `col2` don't have one-to-one cardinality.

    Examples
    --------
    >>> regs = read_registrations_file('tests/registrations.csv')
    >>> check_one_to_one_cardinality(df=regs, col1='local_dataset_id', col2='local_dataset_endpoint')
    """
    df = df[[col1, col2]].drop_duplicates()
    group_counts = pd.concat([df[col1].value_counts(), df[col2].value_counts()])
    replicates = group_counts > 1
    if any(replicates):
        msg = col1 + ' and ' + col2 + ' should have 1-to-1 cardinality. ' + \
              'However, > 1 corresponding element was found for: ' + \
              ', '.join(group_counts[replicates].index.to_list())
        warnings.warn(msg)


def check_group_registrations(regs):
    """Checks uniqueness of dataset group registrations.

    Registrations can be part of a group, the most recent of which is
    considered to be the authoratative version of the series.

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
    If `local_dataset_group_id` and `gbif_dataset_uuid` don't have one-to-one
        cardinality.

    Examples
    --------
    >>> regs = read_registrations_file('tests/registrations.csv')
    >>> check_group_registrations(regs)
    """
    check_one_to_one_cardinality(df=regs, col1='local_dataset_group_id', col2='gbif_dataset_uuid')


def check_local_endpoints(regs):
    """Checks uniqueness of local dataset endpoints.

    Registrations each have a unique endpoint, which is crawled by GBIF and
    referenced to from the associated GBIF dataset page.

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
    If `local_dataset_id` and `local_dataset_endpoint` don't have one-to-one
        cardinality.

    Examples
    --------
    >>> regs = read_registrations_file('tests/registrations.csv')
    >>> check_local_endpoints(regs)
    """
    check_one_to_one_cardinality(df=regs, col1='local_dataset_id', col2='local_dataset_endpoint')


def check_crawl_datetime(regs):
    """Checks if registrations have been crawled.

    Registrations contain all the information needed for GBIF to successfully
    crawl the corresponding dataset and post to the GBIF data portal. Datetime
    values in the `gbif_crawl_datetime` indicate the dataset has been crawled.

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
    If a registration has not yet been crawled.

    Examples
    --------
    >>> regs = read_registrations_file('tests/registrations.csv')
    >>> check_crawl_datetime(regs)
    """
    uncrawled = regs['gbif_crawl_datetime'].isna()
    if any(uncrawled):
        rows = regs[uncrawled].index.to_series() + 1
        rows = rows.astype('string')
        warnings.warn('Uncrawled registrations in rows: ' + ', '.join(rows))


def validate_registrations_file(file_path):
    """Checks registrations for any issues.

    This is a wrapper to `check_completeness`, `check_local_dataset_id`,
    `check_group_registrations`, `check_local_endpoints`, and
    `check_crawl_datetime`.

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
    >>> validate_registrations_file('tests/registrations.csv')
    """
    regs = read_registrations_file(file_path)
    check_completeness(regs)
    check_local_dataset_id(regs)
    check_group_registrations(regs)
    check_local_endpoints(regs)
    check_crawl_datetime(regs)
