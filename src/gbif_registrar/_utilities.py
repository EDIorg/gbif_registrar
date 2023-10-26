"""Utility functions FOR INTERNAL USE ONLY!"""

from os import environ
import json
from json import loads
import warnings
import pandas as pd
from lxml import etree
import requests
from requests import post, get, delete


def _check_completeness(registrations):
    """Checks registrations for completeness.

    A complete registration has values for all fields except (perhaps)
    `synchronized`, which is not essential for initiating a GBIF
    crawl.

    Parameters
    ----------
    registrations : pandas.DataFrame
        A dataframe of the registrations file. Use`_read_registrations_file` to
        create this.

    Returns
    -------
    None

    Warns
    -----
    UserWarning
        If any registrations are incomplete.
    """
    registrations = registrations[_expected_cols()].drop(["synchronized"], axis=1)
    registrations = registrations[registrations.isna().any(axis=1)]
    if len(registrations) > 0:
        rows = registrations.index.to_series() + 1
        rows = rows.astype("string")
        warnings.warn("Incomplete registrations in rows: " + ", ".join(rows))


def _check_group_registrations(registrations):
    """Checks uniqueness of dataset group registrations.

    Registrations can be part of a group, the most recent of which is
    considered to be the authoratative version of the series.

    Parameters
    ----------
    registrations : pandas.DataFrame
        A dataframe of the registrations file. Use`_read_registrations_file` to
        create this.

    Returns
    -------
    None

    Warns
    -----
    If `local_dataset_group_id` and `gbif_dataset_uuid` don't have one-to-one
        cardinality.
    """
    _check_one_to_one_cardinality(
        data=registrations, col1="local_dataset_group_id", col2="gbif_dataset_uuid"
    )


def _check_synchronized(registrations):
    """Checks if registrations have been synchronized.

    Registrations contain all the information needed for GBIF to successfully
    crawl the corresponding dataset and post to the GBIF data portal. Boolean
    True/False values in the `synchronized` field indicate the dataset has been
    synchronized.

    Parameters
    ----------
    registrations : pandas.DataFrame
        A dataframe of the registrations file. Use`_read_registrations_file` to
        create this.

    Returns
    -------
    None

    Warns
    -----
    If a registration has not yet been crawled.
    """
    if not registrations["synchronized"].all():
        rows = registrations["synchronized"].index.to_series() + 1
        rows = rows[~registrations["synchronized"]].astype("string")
        warnings.warn("Unsynchronized registrations in rows: " + ", ".join(rows))


def _check_local_dataset_group_id_format(registrations):
    """Check the format of the local_dataset_group_id.

    registrations : pandas.DataFrame
        A dataframe of the registrations file. Use`_read_registrations_file` to
        create this.

    Returns
    -------
    None

    Warns
    -----
    If local_dataset_group_id does not have the truncated data package ID
    format used by the Environmental Data Initiative (EDI), i.e.
    `scope.identifier`.
    """
    ids = registrations["local_dataset_id"]
    expected_groups = ids.str.extract(r"(\D+\d+)")[0]
    actual_groups = registrations["local_dataset_group_id"]
    res = expected_groups.compare(actual_groups)
    if len(res) > 0:
        rows = res.index.to_series() + 1
        warnings.warn(
            "Invalid local_dataset_group_id values in rows: "
            + ", ".join(rows.astype("string"))
        )


def _check_local_dataset_id(registrations):
    """Checks registrations for unique local_dataset_id.

    Each registration is represented by a unique primary key, i.e. the
    `local_dataset_id`.

    Parameters
    ----------
    registrations : pandas.DataFrame
        A dataframe of the registrations file. Use`_read_registrations_file` to
        create this.

    Returns
    -------
    None

    Warns
    -----
    UserWarning
        If values in the `local_dataset_id` column are not unique.
    """
    dupes = registrations["local_dataset_id"].duplicated()
    if any(dupes):
        dupes = dupes.index.to_series() + 1
        dupes = dupes.astype("string")
        warnings.warn("Duplicate local_dataset_id values in rows: " + ", ".join(dupes))


def _check_local_dataset_id_format(registrations):
    """Check the format of the local_dataset_id.

    Parameters
    ----------
    registrations : pandas.DataFrame
        A dataframe of the registrations file. Use`read_registrations_file` to
        create this.

    Returns
    -------
    None

    Warns
    -----
    If local_dataset_id does not have the data package ID format used by the
    Environmental Data Initiative (EDI), i.e. `scope.identifier.revision`.

    Examples
    --------
    >>> registrations = _read_registrations_file('tests/registrations.csv')
    >>> _check_local_dataset_id_format(registrations)
    """
    ids = registrations["local_dataset_id"]
    bad_ids = ~ids.str.contains(r"^.+\.\d+\.\d+$")
    if any(bad_ids):
        rows = ids[bad_ids].index.to_series() + 1
        warnings.warn(
            "Invalid local_dataset_id values in rows: "
            + ", ".join(rows.astype("string"))
        )


def _check_local_endpoints(registrations):
    """Checks uniqueness of local dataset endpoints.

    Registrations each have a unique endpoint, which is crawled by GBIF and
    referenced to from the associated GBIF dataset page.

    Parameters
    ----------
    registrations : pandas.DataFrame
        A dataframe of the registrations file. Use`_read_registrations_file` to
        create this.

    Returns
    -------
    None

    Warns
    -----
    If `local_dataset_id` and `local_dataset_endpoint` don't have one-to-one
        cardinality.
    """
    _check_one_to_one_cardinality(
        data=registrations, col1="local_dataset_id", col2="local_dataset_endpoint"
    )


def _check_one_to_one_cardinality(data, col1, col2):
    """Check for one-to-one cardinality between two columns of a dataframe.

    This is a helper function used in a couple registration checks.

    Parameters
    ----------
    data : pandas.DataFrame
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
    """
    data = data[[col1, col2]].drop_duplicates()
    group_counts = pd.concat([data[col1].value_counts(), data[col2].value_counts()])
    replicates = group_counts > 1
    if any(replicates):
        msg = (
            col1
            + " and "
            + col2
            + " should have 1-to-1 cardinality. "
            + "However, > 1 corresponding element was found for: "
            + ", ".join(group_counts[replicates].index.to_list())
        )
        warnings.warn(msg)


def _delete_local_dataset_endpoints(gbif_dataset_uuid):
    """Delete all local dataset endpoints from a GBIF dataset.

    Parameters
    ----------
    gbif_dataset_uuid : str
        The registration identifier assigned by GBIF to the local dataset.

    Returns
    -------
    None
        Will raise an exception if the DELETE fails.

    Notes
    -----
    This function requires authentication with GBIF. Use the login function
    from the authenticate module to do this.
    """
    # Get the list of existing endpoints to delete
    endpoints = get(
        environ["GBIF_API"] + "/" + gbif_dataset_uuid + "/endpoint",
        auth=(environ["USER_NAME"], environ["PASSWORD"]),
        headers={"Content-Type": "application/json"},
        timeout=60,
    )
    endpoints.raise_for_status()

    # Delete each endpoint
    if len(endpoints.json()) != 0:
        for item in endpoints.json():
            key = item.get("key")
            resp = delete(
                environ["GBIF_API"] + "/" + gbif_dataset_uuid + "/endpoint/" + str(key),
                auth=(environ["USER_NAME"], environ["PASSWORD"]),
                headers={"Content-Type": "application/json"},
                timeout=60,
            )
            resp.raise_for_status()


def _expected_cols():
    """Expected columns of the registrations file"""
    cols = [
        "local_dataset_id",
        "local_dataset_group_id",
        "local_dataset_endpoint",
        "gbif_dataset_uuid",
        "synchronized",
    ]
    return cols


def _get_gbif_dataset_uuid(local_dataset_group_id, registrations):
    """Return the gbif_dataset_uuid value.

    Parameters
    ----------
    local_dataset_group_id : str
        The dataset group identifier in the EDI repository. Has the format:
        {scope}.{identifier}.
    registrations : pandas dataframe
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
    """
    # Look in the registrations dataframe to see if there is a matching
    # local_data_set_group_id value, and it has a non-empty gbif_dataset_uuid
    # value. If so, get the gbif_dataset_uuid value.
    has_group_id = (
        local_dataset_group_id in registrations["local_dataset_group_id"].values
    )
    has_uuid = (
        registrations.loc[
            registrations["local_dataset_group_id"] == local_dataset_group_id,
            "gbif_dataset_uuid",
        ]
        .notnull()
        .iloc[0]
    )
    if has_group_id and has_uuid:
        gbif_dataset_uuid = registrations.loc[
            registrations["local_dataset_group_id"] == local_dataset_group_id,
            "gbif_dataset_uuid",
        ].iloc[0]
    # If there is no matching local_dataset_group_id value, or if there is a
    # matching local_dataset_group_id value, but it has an empty
    # gbif_dataset_uuid value, then call the register_dataset function to
    # register the dataset with GBIF and get the gbif_dataset_uuid value.
    else:
        gbif_dataset_uuid = _request_gbif_dataset_uuid()
    return gbif_dataset_uuid


def _get_local_dataset_endpoint(local_dataset_id):
    """Return the local_dataset_endpoint value.

    Parameters
    ----------
    local_dataset_id : str
        The dataset identifier in the EDI repository. Has the format:
        {scope}.{identifier}.{revision}.

    Returns
    -------
    str
        The local_dataset_endpoint URL value. This is the URL GBIF will crawl
        to access the local dataset.

    Notes
    -----
    This function requires authentication with GBIF. Use the login function
    from the authenticate module to do this.
    """
    scope = local_dataset_id.split(".")[0]
    identifier = local_dataset_id.split(".")[1]
    revision = local_dataset_id.split(".")[2]
    local_dataset_id = (
        environ["PASTA_ENVIRONMENT"]
        + "/package/download/eml/"
        + scope
        + "/"
        + identifier
        + "/"
        + revision
    )
    return local_dataset_id


def _get_local_dataset_group_id(local_dataset_id):
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


def _is_synchronized(local_dataset_id, file_path):
    """Check if a local dataset is synchronized with the GBIF registry.

    Parameters
    ----------
    local_dataset_id : str
        The identifier of the dataset in the EDI repository. Has the format:
        {scope}.{identifier}.{revision}.
    file_path : str
        Path of the registrations file containing the registration information
        for the local dataset.

    Returns
    -------
    bool
        True if the dataset is synchronized, False otherwise.

    Notes
    -----
    The local dataset is synchronized if the local dataset publication date
    (listed in the EML) and the local dataset endpoint match those of the
    GBIF instance.
    """
    # Get the gbif_dataset_uuid to use in the GBIF API call.
    registrations = _read_registrations_file(file_path)
    gbif_dataset_uuid = registrations.loc[
        registrations["local_dataset_id"] == local_dataset_id, "gbif_dataset_uuid"
    ].values[0]

    # Read the local dataset metadata to get the dataset publication date and
    # endpoint for comparison with the GBIF instance.
    local_metadata = _read_local_dataset_metadata(local_dataset_id)
    local_metadata = etree.fromstring(local_metadata.encode("utf-8"))
    local_pubdate = local_metadata.find("dataset/pubDate").text
    local_endpoint = _get_local_dataset_endpoint(local_dataset_id)

    # Read the GBIF dataset metadata to get the dataset publication date and
    # endpoint for comparison with the local instance.
    gbif_metadata = _read_gbif_dataset_metadata(gbif_dataset_uuid)
    gbif_pubdate = gbif_metadata.get("pubDate")
    gbif_pubdate = gbif_pubdate.split("T")[0]  # PASTA only uses date
    gbif_endpoint = gbif_metadata.get("endpoints")[0].get("url")

    # If the publication dates and endpoints match, the dataset is
    # synchronized.
    pubdate_matches = local_pubdate == gbif_pubdate
    endpoint_matches = local_endpoint == gbif_endpoint
    return pubdate_matches and endpoint_matches


def _post_local_dataset_endpoint(local_dataset_endpoint, gbif_dataset_uuid):
    """Post a local dataset endpoint to GBIF.

    Parameters
    ----------
    local_dataset_endpoint : str
        This is the URL for downloading the dataset (.zip archive) at the EDI
        repository. Use the _get_local_dataset_endpoint function in the
        utilities module to obtain this value.
        gbif_dataset_uuid : str
        The registration identifier assigned by GBIF to the local dataset
        group.

    Returns
    -------
    None
        Will raise an exception if the POST fails.

    Notes
    -----
    This function requires authentication with GBIF. Use the login function
    from the authenticate module to do this.
    """
    my_endpoint = {"url": local_dataset_endpoint, "type": "DWC_ARCHIVE"}
    resp = post(
        environ["GBIF_API"] + "/" + gbif_dataset_uuid + "/endpoint",
        data=json.dumps(my_endpoint),
        auth=(environ["USER_NAME"], environ["PASSWORD"]),
        headers={"Content-Type": "application/json"},
        timeout=60,
    )
    resp.raise_for_status()


def _post_new_metadata_document(local_dataset_id, gbif_dataset_uuid):
    """Post a new metadata document to GBIF.

    Parameters
    ----------
    local_dataset_id : str
        The identifier of the dataset in the EDI repository. Has the format:
        {scope}.{identifier}.{revision}.
    gbif_dataset_uuid : str
        The registration identifier assigned by GBIF to the local dataset
        group.

    Returns
    -------
    None
        Will raise an exception if the POST fails.

    Notes
    -----
    This function requires authentication with GBIF. Use the login function
    from the authenticate module to do this.
    """
    metadata = _read_local_dataset_metadata(local_dataset_id)
    resp = post(
        environ["GBIF_API"] + "/" + gbif_dataset_uuid + "/document",
        data=metadata,
        auth=(environ["USER_NAME"], environ["PASSWORD"]),
        headers={"Content-Type": "application/xml"},
        timeout=60,
    )
    resp.raise_for_status()


def _read_gbif_dataset_metadata(gbif_dataset_uuid):
    """Read the metadata of a GBIF dataset.

    Parameters
    ----------
    gbif_dataset_uuid : str
        The registration identifier assigned by GBIF to the local dataset.

    Returns
    -------
    dict
        A dictionary containing the metadata of the GBIF dataset.

    Notes
    -----
    This is high-level metadata, not the full EML document.

    This function requires authentication with GBIF. Use the login function
    from the authenticate module to do this.
    """
    resp = requests.get(url=environ["GBIF_API"] + "/" + gbif_dataset_uuid, timeout=60)
    if resp.status_code != 200:
        print("HTTP request failed with status code: " + str(resp.status_code))
        print(resp.reason)
        return None
    return loads(resp.text)


def _read_local_dataset_metadata(local_dataset_id):
    """Reads the metadata document for a local dataset.

    Parameters
    ----------
    local_dataset_id : str
        The identifier of the dataset in the EDI repository. Has the format:
        {scope}.{identifier}.{revision}.

    Returns
    -------
    str
        The metadata document for the local dataset in XML format.

    Notes
    -----
    This function requires authentication with GBIF. Use the login function
    from the authenticate module to do this.
    """
    # Build URL for metadata document to be read
    metadata_url = (
        environ["PASTA_ENVIRONMENT"]
        + "/package/metadata/eml/"
        + local_dataset_id.split(".")[0]
        + "/"
        + local_dataset_id.split(".")[1]
        + "/"
        + local_dataset_id.split(".")[2]
    )
    resp = requests.get(metadata_url, timeout=60)
    if resp.status_code != 200:
        print("HTTP request failed with status code: " + str(resp.status_code))
        print(resp.reason)
        return None
    return resp.text


def _read_registrations_file(registrations_file):
    """Return the registrations file as a Pandas dataframe.

    Parameters
    ----------
    registrations_file : str
        Path of the registrations file.

    Returns
    -------
    DataFrame
        The registrations file as a Pandas dataframe.
    """
    registrations = pd.read_csv(
        registrations_file,
        delimiter=",",
        dtype={
            "local_dataset_id": "string",
            "local_dataset_group_id": "string",
            "local_dataset_endpoint": "string",
            "gbif_dataset_uuid": "string",
            "is_synchronized": "boolean",
        },
    )
    return registrations


def _request_gbif_dataset_uuid():
    """Request a GBIF dataset UUID value from GBIF.

    Returns
    -------
    str
        The GBIF dataset UUID value. This is the UUID assigned by GBIF to the
        local dataset group.

    Notes
    -----
    This function requires authentication with GBIF. Use the login function
    from the authenticate module to do this.
    """
    title = "Placeholder title, to be written over by EML metadata from EDI"
    data = {
        "installationKey": environ["INSTALLATION"],
        "publishingOrganizationKey": environ["ORGANIZATION"],
        "type": "SAMPLING_EVENT",
        "title": title,
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(
        url=environ["GBIF_API"],
        data=json.dumps(data),
        auth=(environ["USER_NAME"], environ["PASSWORD"]),
        headers=headers,
        timeout=60,
    )
    if resp.status_code != 201:
        print("HTTP request failed with status code: " + str(resp.status_code))
        print(resp.reason)
        return None
    return resp.json()
