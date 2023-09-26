"""Miscellaneous utilities"""
import os.path
from json import loads
import pandas as pd
from lxml import etree
import requests
from gbif_registrar.config import PASTA_ENVIRONMENT, GBIF_API


def initialize_registrations(file_path):
    """Writes an empty registrations file to path.

    The registrations file is a map from datasets in the local repository, to
    identifiers in the remote GBIF registry. This file contains additional
    information about the local datasets, as well as the synchronization
    status of the local dataset with GBIF. The registrations file columns
    (and definitions):

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
    - `is_synchronized`: The synchronization status of the local dataset with
      GBIF.

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
        data = pd.DataFrame(columns=expected_cols())
        data.to_csv(file_path, index=False, mode="x")


def read_registrations(file_path):
    """Reads the registrations file.

    Parameters
    ----------
    file_path : Any
        Path of the registrations file.

    Returns
    -------
    DataFrame
        Pandas dataframe.

    See Also
    --------
    check_registrations_file
    """
    rgstrs = pd.read_csv(file_path, delimiter=",")
    return rgstrs


def expected_cols():
    """Expected columns of the registrations file"""
    cols = [
        "local_dataset_id",
        "local_dataset_group_id",
        "local_dataset_endpoint",
        "gbif_dataset_uuid",
        "is_synchronized",
    ]
    return cols


def read_local_dataset_metadata(local_dataset_id):
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
    """
    # Build URL for metadata document to be read
    metadata_url = (
        PASTA_ENVIRONMENT
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


def has_metadata(gbif_dataset_uuid):
    """Check if a GBIF dataset has a metadata document.

    Parameters
    ----------
    gbif_dataset_uuid : str
        The registration identifier assigned by GBIF to the local dataset.

    Returns
    -------
    bool
        True if the dataset has a metadata document, False otherwise.

    Notes
    -----
    The presence of a dataset title indicates that the dataset has been
    crawled by GBIF and the metadata document has been created.
    """
    metadata = read_gbif_dataset_metadata(gbif_dataset_uuid)
    if metadata:
        return bool(metadata.get("title"))
    return False


def read_gbif_dataset_metadata(gbif_dataset_uuid):
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
    """
    resp = requests.get(url=GBIF_API + "/" + gbif_dataset_uuid, timeout=60)
    if resp.status_code != 200:
        print("HTTP request failed with status code: " + str(resp.status_code))
        print(resp.reason)
        return None
    return loads(resp.text)


def is_synchronized(local_dataset_id, file_path):
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
    registrations = read_registrations(file_path)
    gbif_dataset_uuid = registrations.loc[
        registrations["local_dataset_id"] == local_dataset_id, "gbif_dataset_uuid"
    ].values[0]

    # Read the local dataset metadata to get the dataset publication date and
    # endpoint for comparison with the GBIF instance.
    local_metadata = read_local_dataset_metadata(local_dataset_id)
    local_metadata = etree.fromstring(local_metadata.encode("utf-8"))
    local_pubdate = local_metadata.find("dataset/pubDate").text
    local_endpoint = get_local_dataset_endpoint(local_dataset_id)

    # Read the GBIF dataset metadata to get the dataset publication date and
    # endpoint for comparison with the local instance.
    gbif_metadata = read_gbif_dataset_metadata(gbif_dataset_uuid)
    gbif_pubdate = gbif_metadata.get("pubDate")
    gbif_pubdate = gbif_pubdate.split("T")[0]  # PASTA only uses date
    gbif_endpoint = gbif_metadata.get("endpoints")[0].get("url")

    # If the publication dates and endpoints match, the dataset is
    # synchronized.
    pubdate_matches = local_pubdate == gbif_pubdate
    endpoint_matches = local_endpoint == gbif_endpoint
    return pubdate_matches and endpoint_matches


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
    local_dataset_id = (
        PASTA_ENVIRONMENT
        + "/package/download/eml/"
        + scope
        + "/"
        + identifier
        + "/"
        + revision
    )
    return local_dataset_id
