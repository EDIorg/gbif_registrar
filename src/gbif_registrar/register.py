"""Functions for registering datasets with GBIF."""
import os.path
import tempfile
import json
import requests
import pandas as pd
from gbif_registrar.config import (
    GBIF_API,
    INSTALLATION,
    ORGANIZATION,
    PASSWORD,
    USER_NAME,
)
from gbif_registrar.utilities import read_registrations_file
from gbif_registrar.utilities import get_local_dataset_endpoint
from gbif_registrar.utilities import expected_cols


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
        data = pd.DataFrame(columns=expected_cols())
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

    Examples
    --------
    >>> register_dataset("edi.929.2", "registrations.csv")
    """
    registrations = read_registrations_file(registrations_file)
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
                "local_dataset_group_id": None,
                "local_dataset_endpoint": None,
                "gbif_dataset_uuid": None,
                "is_synchronized": None,
            },
            index=[0],
        )
        # Write the new_record dataframe to a .csv file in the temp directory
        # so that the complete_registration_records function can read it.
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=True) as temp_file:
            new_record.to_csv(temp_file.name, index=False, mode="w")
            complete_registration_records(temp_file.name)
            new_record = read_registrations_file(temp_file.name)
        registrations = pd.concat([registrations, new_record], ignore_index=True)
        registrations.to_csv(registrations_file, index=False, mode="w")
    return None


def complete_registration_records(registrations_file):
    """Return a completed set of registration records.

    This function can be run to repair one or more registrations that have
    missing values in the local_dataset_group_id, local_dataset_endpoint, or
    gbif_dataset_uuid columns.

    Parameters
    ----------
    registrations_file : str
        The path of the registrations file.

    Returns
    -------
    None
        The registrations file, written back to `registrations_file` as a .csv.

    Examples
    --------
    >>> complete_registration_records("registrations.csv")
    """
    registrations = read_registrations_file(registrations_file)
    # Get all rows where the registrations dataframe columns
    # local_dataset_group_id, local_dataset_endpoint, gbif_dataset_uuid,
    # is_synchronized contain empty values. These are the rows
    # that need to be completed.
    record = registrations[
        (registrations["local_dataset_group_id"].isnull())
        | (registrations["local_dataset_endpoint"].isnull())
        | (registrations["gbif_dataset_uuid"].isnull())
        | (registrations["is_synchronized"].isnull())
    ]
    # If the record dataframe is empty, then there are no rows to complete.
    # Return the registrations dataframe.
    if record.empty:
        return None
    # If the record dataframe is not empty, then there are rows to complete.
    # Iterate through the rows of the record dataframe.
    for index, row in record.iterrows():
        # If the local_dataset_group_id column is empty, then call the
        # get_local_dataset_group_id function to get the local_dataset_group_id
        # value and insert it into the local_dataset_group_id column of the
        # registrations dataframe.
        if pd.isnull(row["local_dataset_group_id"]):
            local_dataset_group_id = get_local_dataset_group_id(
                local_dataset_id=row["local_dataset_id"]
            )
            # Add the local_dataset_group_id value to the
            # local_dataset_group_id column of the registrations dataframe.
            registrations.loc[index, "local_dataset_group_id"] = local_dataset_group_id
        # If the local_dataset_endpoint column is empty, then call the
        # get_local_dataset_endpoint function to get the local_dataset_endpoint
        # value and insert it into the local_dataset_endpoint column of the
        # registrations dataframe.
        if pd.isnull(row["local_dataset_endpoint"]):
            local_dataset_endpoint = get_local_dataset_endpoint(
                local_dataset_id=row["local_dataset_id"]
            )
            # Add the local_dataset_endpoint value to the
            # local_dataset_endpoint column of the registrations dataframe.
            registrations.loc[index, "local_dataset_endpoint"] = local_dataset_endpoint
        # If the gbif_dataset_uuid column is empty, then call the
        # get_gbif_dataset_uuid function to get the gbif_dataset_uuid value and
        # insert it into the gbif_dataset_uuid column of the registrations
        # dataframe.
        if pd.isnull(row["gbif_dataset_uuid"]):
            gbif_dataset_uuid = get_gbif_dataset_uuid(
                local_dataset_group_id=registrations.loc[
                    index, "local_dataset_endpoint"
                ],
                rgstrs=registrations,
            )
            # Add the gbif_dataset_uuid value to the gbif_dataset_uuid column
            # of the registrations dataframe.
            registrations.loc[index, "gbif_dataset_uuid"] = gbif_dataset_uuid
    registrations.to_csv(registrations_file, index=False, mode="w")
    return None


def get_local_dataset_group_id(local_dataset_id):
    """Return the local_dataset_group_id value.

    Parameters
    ----------
    local_dataset_id : str
        The dataset identifier in the EDI repository. Has the format:
        {scope}.{identifier}.{revision}.

    Returns
    -------
    str
        The local_dataset_group_id value.
    """
    # The local_dataset_group_id value is derived by dropping the last period
    # and everything after it from the local_dataset_id value.
    local_dataset_group_id = local_dataset_id.rsplit(".", 1)[0]
    return local_dataset_group_id


def get_gbif_dataset_uuid(local_dataset_group_id, rgstrs):
    """Return the gbif_dataset_uuid value.

    Parameters
    ----------
    local_dataset_group_id : str
        The dataset group identifier in the EDI repository. Has the format:
        {scope}.{identifier}.
    rgstrs : pandas dataframe
        The registrations file as a dataframe.


    Returns
    -------
    str
        The gbif_dataset_uuid value. This is the UUID assigned by GBIF to the
        local dataset group identifier. A new value will be returned if a
        gbif_dataset_uuid value doesn't already exist for a
        local_dataset_group_id.

    Notes
    -----
    The local_dataset_group_id and gbif_dataset_uuid values have a one-to-one
    relationship because this allows a dataset series (i.e. multiple versions
    of a dataset) to be registered with GBIF as a single dataset and displayed
    from a single URL endpoint on the GBIF system.

    Examples
    --------
    >>> registrations = read_registrations_file("registrations.csv")
    >>> get_gbif_dataset_uuid("edi.929", registrations)
    """
    # Look in the rgstrs dataframe to see if there is a matching
    # local_data_set_group_id value, and it has a non-empty gbif_dataset_uuid
    # value. If so, get the gbif_dataset_uuid value.
    has_group_id = local_dataset_group_id in rgstrs["local_dataset_group_id"].values
    has_uuid = (
        rgstrs.loc[
            rgstrs["local_dataset_group_id"] == local_dataset_group_id,
            "gbif_dataset_uuid",
        ]
        .notnull()
        .iloc[0]
    )
    if has_group_id and has_uuid:
        gbif_dataset_uuid = rgstrs.loc[
            rgstrs["local_dataset_group_id"] == local_dataset_group_id,
            "gbif_dataset_uuid",
        ].iloc[0]
    # If there is no matching local_dataset_group_id value, or if there is a
    # matching local_dataset_group_id value, but it has an empty
    # gbif_dataset_uuid value, then call the register_dataset function to
    # register the dataset with GBIF and get the gbif_dataset_uuid value.
    else:
        gbif_dataset_uuid = request_gbif_dataset_uuid()
    return gbif_dataset_uuid


def request_gbif_dataset_uuid():
    """Request a GBIF dataset UUID value from GBIF.

    Returns
    -------
    str
        The GBIF dataset UUID value. This is the UUID assigned by GBIF to the
        local dataset group.
    """
    title = "Placeholder title, to be written over by EML metadata from EDI"
    data = {
        "installationKey": INSTALLATION,
        "publishingOrganizationKey": ORGANIZATION,
        "type": "SAMPLING_EVENT",
        "title": title,
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(
        url=GBIF_API,
        data=json.dumps(data),
        auth=(USER_NAME, PASSWORD),
        headers=headers,
        timeout=60,
    )
    if resp.status_code != 201:
        print("HTTP request failed with status code: " + str(resp.status_code))
        print(resp.reason)
        return None
    return resp.json()
