"""Miscellaneous utilities"""
import os.path
import pandas as pd


def initialize_registrations(file_path):
    """Writes an empty registrations file to path.

    The registrations file is a map from datasets in the local repository, to
    identifiers in the remote GBIF registry. This file contains additional
    information about the local datasets, as well as the most recent datetime
    GBIF crawled the local endpoint to synchronize the registry instance. The
    registrations file columns (and definitions):

    - `local_dataset_id`: The identifier of the dataset in the local
      repository system. This is the primary key.
    - `local_dataset_group_id`: An identifier for grouping datasets of the
      same series. This can form a one-to-many relationship with
      local_dataset_id.
    - `local_dataset_endpoint`: The endpoint for the local dataset to be
      crawled by GBIF. This generally has a one-to-one relationship with
      `local_dataset_id`.
    - `gbif_dataset_uuid`: The registration identifier assigned by GBIF to the
      local dataset group. This has a one-to-one relationship with
      `local_dataset_group_id`.
    - `gbif_endpoint_set_datetime`: The datetime GBIF crawled the
      `local_dataset_endpoint`.

    Parameters
    ----------
    file_path : Any
        Path of file to be written. A .csv file extension is expected.

    Returns
    -------
    None
        The registrations file as a .csv.
    """
    if os.path.exists(file_path):
        pass
    else:
        cols = [
            "local_dataset_id",
            "local_dataset_group_id",
            "local_dataset_endpoint",
            "gbif_dataset_uuid",
            "gbif_endpoint_set_datetime"
        ]
        df = pd.DataFrame(columns=cols)
        df.to_csv(file_path, index=False, mode="x")


def read_registrations(file_path):
    """Reads the registrations file.

    Parameters
    ----------
    file_path : Any
        Path of the registrations file.

    Returns
    -------
    DataFrame
        Pandas dataframe with the gbif_endpoint_set_datetime column formatted as
        datetime.

    See Also
    --------
    check_registrations_file
    """
    rgstrs = pd.read_csv(file_path, delimiter=",")
    rgstrs["gbif_endpoint_set_datetime"] = pd.to_datetime(
        rgstrs["gbif_endpoint_set_datetime"])
    return rgstrs


def expected_cols():
    """Expected columns of the registrations file"""
    cols = [
        "local_dataset_id",
        "local_dataset_group_id",
        "local_dataset_endpoint",
        "gbif_dataset_uuid",
        "gbif_endpoint_set_datetime",
    ]
    return cols
