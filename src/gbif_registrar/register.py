"""Functions for registering datasets with GBIF."""
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
    """Returns an empty registrations file.

    The registrations file maps datasets from the local EDI data repository to
    the remote GBIF registry and indicates synchronization status between the
    two.

    Parameters
    ----------
    file_path : str
        Path of file to be written. A .csv file extension is expected.

    Returns
    -------
    None
        The registrations file as a .csv.

    Notes
    -----
    The registrations file columns and definitions are as follows:

    - `local_dataset_id`: The dataset identifier in the EDI repository. This
      is the primary key. The term 'dataset' used here, is synonymous with the
      term 'data package' in the EDI repository.
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
    - `is_synchronized`: The synchronization status of the `local_dataset_id`
      with GBIF. Is `True` if the local dataset is synchronized with GBIF, and
      `False` if the local dataset is not synchronized with GBIF. This forms
      a one-to-one relationship with `local_dataset_id`.

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
    """Register a local dataset with GBIF and add it to the registrations file.

    Parameters
    ----------
    local_dataset_id : str
        The dataset identifier in the EDI repository. Has the format:
        {scope}.{identifier}.{revision}.
    registrations_file : str
        The path of the registrations file.

    Returns
    -------
    None
        The registrations file, written back to `registrations_file` as a .csv.

    Notes
    -----
    This function requires authentication with GBIF. Use the load_configuration function
    from the authenticate module to do this.

    Examples
    --------
    >>> register_dataset("edi.929.2", "registrations.csv")
    """
    registrations = _read_registrations_file(registrations_file)
    # If the local_dataset_id already exists in the registrations file, then
    # there's no work to be done, so return the registrations file as-is.
    if local_dataset_id in set(registrations["local_dataset_id"]):
        registrations.to_csv(registrations_file, index=False, mode="w")
        return None
    # Create a oneline dataframe with the local_dataset_id for
    # complete_registrations to operate on (passing a full dataframe results
    # in iterative registration attempts on other listed local_dataset_id),
    # append the result to the full registrations data frame and return to the
    # user.
    if local_dataset_id is not None:  # None is invalid and will cause an error
        new_record = pd.DataFrame(
            {
                "local_dataset_id": local_dataset_id,
                "synchronized": False,
            },
            index=[0],
        )
        # Add the new record to the registrations dataframe and write it to
        # the temp directory as a .csv file so that the
        # complete_registration_records function can read it.
        registrations = pd.concat([registrations, new_record], ignore_index=True)
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=True) as temp_file:
            registrations.to_csv(temp_file.name, index=False, mode="w")
            complete_registration_records(temp_file.name, local_dataset_id)
            registrations = _read_registrations_file(temp_file.name)
        registrations.to_csv(registrations_file, index=False, mode="w")
    return None


def complete_registration_records(registrations_file, local_dataset_id=None):
    """Return a completed set of registration records.

    This function can be run to repair one or more registrations that have
    missing values in the local_dataset_group_id, local_dataset_endpoint, or
    gbif_dataset_uuid columns.

    Parameters
    ----------
    registrations_file : str
        The path of the registrations file.
    local_dataset_id : str, optional
        The dataset identifier in the EDI repository. Has the format:
        {scope}.{identifier}.{revision}. If provided, only the registration
        record for the local_dataset_id will be completed. If not provided,
        all registration records with missing values will be completed.

    Returns
    -------
    None
        The registrations file, written back to `registrations_file` as a .csv.

    Notes
    -----
    This function requires authentication with GBIF. Use the load_configuration function
    from the authenticate module to do this.

    Examples
    --------
    >>> # Complete all registration records with missing values.
    >>> complete_registration_records("registrations.csv")
    >>> # Complete the registration record for the local_dataset_id.
    >>> complete_registration_records("registrations.csv", "edi.929.2")
    """
    registrations = _read_registrations_file(registrations_file)
    # Get all rows where the registrations dataframe columns
    # local_dataset_group_id, local_dataset_endpoint, gbif_dataset_uuid,
    # synchronized contain empty values. These are the rows
    # that need to be completed.
    record = registrations[
        (registrations["local_dataset_group_id"].isna())
        | (registrations["local_dataset_endpoint"].isna())
        | (registrations["gbif_dataset_uuid"].isna())
    ]
    # If the record dataframe is empty, then there are no rows to complete.
    # Return the registrations dataframe.
    if record.empty:
        return None
    # Only operate on the registration record for the local_dataset_id if it
    # was provided.
    if local_dataset_id is not None:
        if local_dataset_id not in set(record["local_dataset_id"]):
            return None
        record = record[record["local_dataset_id"] == local_dataset_id]
    # If the record dataframe is not empty, then there are rows to complete.
    # Iterate through the rows of the record dataframe.
    for index, row in record.iterrows():
        # If the local_dataset_group_id column is empty, then call the
        # _get_local_dataset_group_id function to get the local_dataset_group_id
        # value and insert it into the local_dataset_group_id column of the
        # registrations dataframe.
        if pd.isna(row["local_dataset_group_id"]):
            local_dataset_group_id = _get_local_dataset_group_id(
                local_dataset_id=row["local_dataset_id"]
            )
            # Add the local_dataset_group_id value to the
            # local_dataset_group_id column of the registrations dataframe.
            registrations.loc[index, "local_dataset_group_id"] = local_dataset_group_id
        # If the local_dataset_endpoint column is empty, then call the
        # _get_local_dataset_endpoint function to get the local_dataset_endpoint
        # value and insert it into the local_dataset_endpoint column of the
        # registrations dataframe.
        if pd.isna(row["local_dataset_endpoint"]):
            local_dataset_endpoint = _get_local_dataset_endpoint(
                local_dataset_id=row["local_dataset_id"]
            )
            # Add the local_dataset_endpoint value to the
            # local_dataset_endpoint column of the registrations dataframe.
            registrations.loc[index, "local_dataset_endpoint"] = local_dataset_endpoint
        # If the gbif_dataset_uuid column is empty, then call the
        # _get_gbif_dataset_uuid function to get the gbif_dataset_uuid value and
        # insert it into the gbif_dataset_uuid column of the registrations
        # dataframe.
        if pd.isna(row["gbif_dataset_uuid"]):
            gbif_dataset_uuid = _get_gbif_dataset_uuid(
                local_dataset_group_id=registrations.loc[
                    index, "local_dataset_group_id"
                ],
                registrations=registrations,
            )
            # Add the gbif_dataset_uuid value to the gbif_dataset_uuid column
            # of the registrations dataframe.
            registrations.loc[index, "gbif_dataset_uuid"] = gbif_dataset_uuid
    registrations.to_csv(registrations_file, index=False, mode="w")
    return None
