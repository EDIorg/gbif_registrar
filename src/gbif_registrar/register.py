"""Functions for registering datasets with GBIF."""
import json
import uuid
import requests
import pandas as pd
from gbif_registrar import config
from gbif_registrar.utilities import read_registrations


def register(file_path, local_dataset_id=None):
    """Register a local_dataset_id with GBIF. This is required before
    requesting a crawl.

    Parameters
    ----------
    file_path : str
        Path of the registrations file.
    local_dataset_id : str
        Identifier of the local dataset to be registered with GBIF. Run with
        local_dataset_id argument when registering for the first time, or run
        with local_dataset_id=None to fix incomplete registrations.

    Returns
    -------
    None
        The registrations file as a .csv.

    Notes
    -----
    Running this function will overwrite the existing registrations file at
    `file_path`.

    This function has subroutines that insert a local_dataset_group_id and
    local_dataset_endpoint based on specifications of the local system. These
    parts of the source code can be edited to accommodate your local system.
    """
    # Read the registrations file from the file path parameter
    rgstrs = read_registrations(file_path)
    # If the local_dataset_id already exists in the registrations file, then
    # return the registrations file as-is and send to complete_registrations
    # function for further processing.
    if local_dataset_id not in set(rgstrs["local_dataset_id"]):
        # If the local_dataset_id parameter is not None, then append the
        # local__dataset_id value to the rgstrs data frame in a new row and in
        # the local_dataset_id column. The other columns should be empty at this
        # point.
        if local_dataset_id is not None:
            new_row = pd.DataFrame(
                {
                    "local_dataset_id": local_dataset_id,
                    "local_dataset_group_id": None,
                    "local_dataset_endpoint": None,
                    "gbif_dataset_uuid": None,
                    "gbif_endpoint_set_datetime": None,
                },
                index=[0],
            )
            rgstrs = pd.concat([rgstrs, new_row], ignore_index=True)
    # Call the complete_registrations function to complete the registration
    rgstrs = complete_registrations(rgstrs)
    # Write the completed registrations file to the file path parameter
    rgstrs.to_csv(file_path, index=False, mode="w")


def complete_registrations(rgstrs):
    """Complete the registration of a local_dataset_id with GBIF.

    Parameters
    ----------
    rgstrs : DataFrame
        Pandas dataframe with the gbif_endpoint_set_datetime column formatted as
        datetime.

    Returns
    -------
    DataFrame
        Pandas dataframe with other columns completed.
    """
    # Get all rows where the rgstrs dataframe columns
    # local_dataset_group_id, local_dataset_endpoint, gbif_dataset_uuid,
    # gbif_endpoint_set_datetime contain empty values. These are the rows
    # that need to be completed.
    record = rgstrs[
        (rgstrs["local_dataset_group_id"].isnull())
        | (rgstrs["local_dataset_endpoint"].isnull())
        | (rgstrs["gbif_dataset_uuid"].isnull())
        | (rgstrs["gbif_endpoint_set_datetime"].isnull())
    ]
    # If the record dataframe is empty, then there are no rows to complete.
    # Return the rgstrs dataframe.
    if record.empty:
        return rgstrs
    # If the record dataframe is not empty, then there are rows to complete.
    # Iterate through the rows of the record dataframe.
    for index, row in record.iterrows():
        # If the local_dataset_group_id column is empty, then call the
        # get_local_dataset_group_id function to get the local_dataset_group_id
        # value and insert it into the local_dataset_group_id column of the
        # rgstrs dataframe.
        if pd.isnull(row["local_dataset_group_id"]):
            local_dataset_group_id = get_local_dataset_group_id(
                local_dataset_id=row["local_dataset_id"]
            )
            # Add the local_dataset_group_id value to the local_dataset_group_id
            # column of the rgstrs dataframe.
            rgstrs.loc[index, "local_dataset_group_id"] = local_dataset_group_id
        # If the local_dataset_endpoint column is empty, then call the
        # get_local_dataset_endpoint function to get the local_dataset_endpoint
        # value and insert it into the local_dataset_endpoint column of the
        # rgstrs dataframe.
        if pd.isnull(row["local_dataset_endpoint"]):
            local_dataset_endpoint = get_local_dataset_endpoint(
                local_dataset_id=row["local_dataset_id"]
            )
            # Add the local_dataset_endpoint value to the local_dataset_endpoint
            # column of the rgstrs dataframe.
            rgstrs.loc[index, "local_dataset_endpoint"] = local_dataset_endpoint
        # If the gbif_dataset_uuid column is empty, then call the
        # get_gbif_dataset_uuid function to get the gbif_dataset_uuid value and
        # insert it into the gbif_dataset_uuid column of the rgstrs dataframe.
        if pd.isnull(row["gbif_dataset_uuid"]):
            gbif_dataset_uuid = get_gbif_dataset_uuid(
                local_dataset_group_id=rgstrs.loc[index, "local_dataset_endpoint"],
                rgstrs=rgstrs,
            )
            # Add the gbif_dataset_uuid value to the gbif_dataset_uuid column of
            # the rgstrs dataframe.
            rgstrs.loc[index, "gbif_dataset_uuid"] = gbif_dataset_uuid
    return rgstrs


def get_local_dataset_group_id(local_dataset_id):
    """Get the local_dataset_group_id value.

    Parameters
    ----------
    local_dataset_id : str
        Identifier of the local dataset to be registered with GBIF. The
        local_dataset_group_id value is derived from this value.

    Returns
    -------
    str
        The local_dataset_group_id value.
    """
    # The local_dataset_group_id value is derived by dropping the last period
    # and everything after it from the local_dataset_id value.
    local_dataset_group_id = local_dataset_id.rsplit(".", 1)[0]
    return local_dataset_group_id


def get_local_dataset_endpoint(local_dataset_id):
    """Get the local_dataset_endpoint value.

    Parameters
    ----------
    local_dataset_id : str
        Identifier of the local dataset to be registered with GBIF. The
        local_dataset_endpoint value is derived from this value.

    Returns
    -------
    str
        The local_dataset_endpoint URL value. This is the URL GBIF will crawl
        to access the local dataset.
    """
    scope = local_dataset_id.split(".")[0]
    identifier = local_dataset_id.split(".")[1]
    revision = local_dataset_id.split(".")[2]
    base_url = "https://pasta.lternet.edu/package/docs/api#GET%20:%20/download/eml/"
    local_dataset_id = base_url + scope + "/" + identifier + "/" + revision
    return local_dataset_id


def get_gbif_dataset_uuid(local_dataset_group_id, rgstrs):
    """Get the gbif_dataset_uuid value.

    Parameters
    ----------
    local_dataset_group_id : str
        Identifier of the local dataset group to be registered with GBIF. The
        gbif_dataset_uuid value is created by GBIF and returned upon request.
    rgstrs : pandas dataframe
        The registrations file as a dataframe.


    Returns
    -------
    str
        The gbif_dataset_uuid value. This is the UUID assigned by GBIF to the
        local dataset group. A new value will be returned if a
        gbif_dataset_uuid value doesn't already exist for a
        local_dataset_group_id.

    Notes
    -----
     The local_dataset_group_id and gbif_dataset_uuid values have a one-to-one
     relationship because this allows a dataset series (i.e. multiple versions
     of a dataset) to be registered with GBIF as a single dataset and displayed
     from a single URL endpoint on the GBIF system.

     The rgstrs dataframe is used to check if a gbif_dataset_uuid value already
     exists for a local_dataset_group_id. If a gbif_dataset_uuid value already
     exists for a local_dataset_group_id, then the existing gbif_dataset_uuid
     value is returned. If a gbif_dataset_uuid value does not already exist
     for a local_dataset_group_id, then a new gbif_dataset_uuid value is
     created and returned.
    """
    # Look in the rgstrs dataframe to see if there is a matching
    # local_data_set_group_id value, and it has a non-empty gbif_dataset_uuid
    # value. If so, get the gbif_dataset_uuid value.
    if local_dataset_group_id in rgstrs["local_dataset_group_id"].values:
        gbif_dataset_uuid = rgstrs.loc[
            rgstrs["local_dataset_group_id"] == local_dataset_group_id,
            "gbif_dataset_uuid",
        ].iloc[0]
    # If there is no matching local_dataset_group_id value, or if there is a
    # matching local_dataset_group_id value but it has an empty
    # gbif_dataset_uuid value, then call the register_dataset function to
    # register the dataset with GBIF and get the gbif_dataset_uuid value.
    else:
        gbif_dataset_uuid = request_gbif_dataset_uuid()
    return gbif_dataset_uuid


def request_gbif_dataset_uuid():
    """Request a gbif_dataset_uuid value from GBIF.

    Returns
    -------
    str
        The gbif_dataset_uuid value. This is the UUID assigned by GBIF to the
        local dataset group.

    Notes
    -----
    The gbif_dataset_uuid value is an arbitrary UUID value generated and
    returned by the GBIF server.
    """
    # TODO: Get title from EML metadata? The request for this information by
    #  GBIF suggests that they are expecting the title to be a static value,
    #  where in fact, EDI's dataset title value can change across versions
    #  within a series. This presents a potential conflict between the
    #  presumably static nature of GBIFS dataset UUID identifier and EDIs
    #  usage of it.
    title = "Placeholder title, to be written over by EML metadata from EDI"
    gbif_endpoint = "http://api.gbif-uat.org/v1/dataset"
    data = {
        "installationKey": config.installation,
        "publishingOrganizationKey": config.organization,
        "type": "SAMPLING_EVENT",
        "title": title,
    }
    headers = {"Content-Type": "application/json"}
    create_dataset = requests.post(
        url=gbif_endpoint,
        data=json.dumps(data),
        auth=(config.username, config.password),
        headers=headers,
        timeout=60,
    )
    # Send a warning if the request was not successful so that the user can
    # check the response and take appropriate action.
    if create_dataset.status_code != 200:
        # FIXME: Declare an exception for better message handling.
        # print("Warning: GBIF dataset registration request failed.")
        gbif_uuid = None
    else:
        dataset_response = create_dataset.json()
        gbif_uuid = dataset_response
    gbif_uuid = str(
        uuid.uuid4()
    )  # TODO Replace this stub once the GBIF API call is working
    return gbif_uuid
