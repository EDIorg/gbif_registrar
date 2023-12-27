"""Register datasets with GBIF."""

import os.path
import tempfile
import pandas as pd
from gbif_registrar._utilities import (
    _get_local_dataset_endpoint,
    _expected_cols,
    _get_local_dataset_group_id,
    _get_gbif_dataset_uuid,
    _read_registrations_file,
)


def initialize_registrations_file(file_path):
    """Returns a template registrations file to path.

    The registrations file maps datasets from the local EDI data repository to
    the remote GBIF registry.

    Parameters
    ----------
    file_path : str
        Path of file to be written. A .csv file extension is expected.

    Returns
    -------
    None
        Writes the template registrations file to disk as a .csv.

    Notes
    -----
    The registrations file columns and definitions are as follows:

    - `local_dataset_id`: The dataset identifier in the EDI repository. This
      is the primary key. The term 'dataset' used here, is synonymous with the
      term 'data package' in the EDI repository. Values in this column have
      the format: {scope}.{identifier}.{revision}.
    - `local_dataset_group_id`: The dataset group identifier in the EDI
      repository. This often forms a one-to-many relationship with
      `local_dataset_id`. The term 'dataset group' used here, is synonymous
      with the term 'data package series' in the EDI repository.
    - `local_dataset_endpoint`: The endpoint for downloading the dataset from
      the EDI repository. This forms a one-to-one relationship with
      `local_dataset_id`.
    - `gbif_dataset_uuid`: The registration identifier assigned by GBIF to the
      `local_dataset_group_id`. This forms a one-to-one relationship with
      `local_dataset_group_id`.
    - `synchronized`: The synchronization status of the `local_dataset_id`
      with GBIF. Is `True` if the local dataset is synchronized with GBIF, and
      `False` if the local dataset is not synchronized with GBIF. This forms
      a one-to-one relationship with `local_dataset_id`. Note, older dataset
      versions that have previously been synchronized will continue to have
      a `True` status, even though they are no longer hosted on GBIF.

    Examples
    --------
    >>> initialize_registrations_file("registrations.csv")
    """
    if os.path.exists(file_path):
        pass
    else:
        data = pd.DataFrame(columns=_expected_cols())
        data.to_csv(file_path, index=False, mode="x")


def register_dataset(local_dataset_id, registrations_file):
    """Registers a local dataset with GBIF and adds it to the registrations
    file.

    Parameters
    ----------
    local_dataset_id : str
        The local dataset identifier.
    registrations_file : str
        The path of the registrations file.

    Returns
    -------
    None
        The registrations file, written back to itself as a .csv.

    Notes
    -----
    This function requires authentication with GBIF. Use the load_configuration
    function from the configure module to do this.

    Examples
    --------
    >>> register_dataset("edi.929.2", "registrations.csv")
    """
    registrations = _read_registrations_file(registrations_file)
    # Return the registrations file "as is" if there is no work to be done
    # (the local_dataset_id is already in the registrations file).
    if local_dataset_id in set(registrations["local_dataset_id"]):
        registrations.to_csv(registrations_file, index=False, mode="w")
        return None
    # Initialize a registration record for the local_dataset_id so it can be
    # added to the registrations dataframe and passed to the
    # complete_registration_records function to operate on.
    if local_dataset_id is not None:  # None is invalid and will cause an error
        new_record = pd.DataFrame(
            {
                "local_dataset_id": local_dataset_id,
                "synchronized": False,
            },
            index=[0],
        )
        registrations = pd.concat([registrations, new_record], ignore_index=True)
        # Write the dataframe to file for complete_registration_records.
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=True) as temp_file:
            registrations.to_csv(temp_file.name, index=False, mode="w")
            complete_registration_records(temp_file.name, local_dataset_id)
            registrations = _read_registrations_file(temp_file.name)
        registrations.to_csv(registrations_file, index=False, mode="w")
    return None


def complete_registration_records(registrations_file, local_dataset_id=None):
    """Returns a completed set of registration records.

    This function can be run to repair one or more dataset registrations that
    have incomplete information in the local_dataset_group_id,
    local_dataset_endpoint, or gbif_dataset_uuid columns.

    Parameters
    ----------
    registrations_file : str
        The path of the registrations file.
    local_dataset_id : str, optional
        The dataset identifier in the EDI repository. If provided, only the
        registration record for the specified `local_dataset_id` will be
        completed. If not provided, all registration records with incomplete
        information will be repaired.

    Returns
    -------
    None
        The registrations file, written back to itself as a .csv.

    Notes
    -----
    This function requires authentication with GBIF. Use the load_configuration
    function from the configure module to do this.

    Examples
    --------
    >>> # Complete all registration records with missing values.
    >>> complete_registration_records("registrations.csv")
    >>> # Repair the registration record for a specific dataset.
    >>> complete_registration_records("registrations.csv", "edi.929.2")
    """
    registrations = _read_registrations_file(registrations_file)
    # Identify incomplete records to fix.
    record = registrations[
        (registrations["local_dataset_group_id"].isna())
        | (registrations["local_dataset_endpoint"].isna())
        | (registrations["gbif_dataset_uuid"].isna())
    ]
    # Return the registrations dataframe "as is" if there's nothing to fix.
    if record.empty:
        return None
    # Narrow down the list of records to fix if specified by the user.
    if local_dataset_id is not None:
        if local_dataset_id not in set(record["local_dataset_id"]):
            return None
        record = record[record["local_dataset_id"] == local_dataset_id]
    # Iterate through incomplete records to fix.
    for index, row in record.iterrows():
        # Fix the record's local_dataset_group_id.
        if pd.isna(row["local_dataset_group_id"]):
            local_dataset_group_id = _get_local_dataset_group_id(
                local_dataset_id=row["local_dataset_id"]
            )
            registrations.loc[index, "local_dataset_group_id"] = local_dataset_group_id
        # Fix the record's local_dataset_endpoint.
        if pd.isna(row["local_dataset_endpoint"]):
            local_dataset_endpoint = _get_local_dataset_endpoint(
                local_dataset_id=row["local_dataset_id"]
            )
            registrations.loc[index, "local_dataset_endpoint"] = local_dataset_endpoint
        # Fix the record's gbif_dataset_uuid.
        if pd.isna(row["gbif_dataset_uuid"]):
            gbif_dataset_uuid = _get_gbif_dataset_uuid(
                local_dataset_group_id=registrations.loc[
                    index, "local_dataset_group_id"
                ],
                registrations=registrations,
            )
            registrations.loc[index, "gbif_dataset_uuid"] = gbif_dataset_uuid
    registrations.to_csv(registrations_file, index=False, mode="w")
    return None
