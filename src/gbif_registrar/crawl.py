"""Functions for calling a GBIF crawl."""

import json
from requests import post, get, delete
from gbif_registrar.config import USER_NAME, PASSWORD, GBIF_API, REGISTRY_BASE_URL
from gbif_registrar.utilities import read_local_dataset_metadata, has_metadata


def initiate_crawl(local_dataset_id, local_dataset_endpoint, gbif_dataset_uuid):
    """Initiate a crawl for a dataset at GBIF.

    Parameters
    ----------
    local_dataset_id : str
        The identifier of the dataset in the EDI repository. Has the format:
        {scope}.{identifier}.{revision}.
    local_dataset_endpoint : str
        This is the URL for downloading the dataset (.zip archive) at the EDI
        repository. This value can be obtained from the
        get_local_dataset_endpoint function in the utilities module.
    gbif_dataset_uuid : str
        The registration identifier assigned by GBIF to the local dataset
        group.

    Returns
    -------
    None
        The registrations file as a .csv.
    """
    # Notify user of the dataset being crawled and provide link to the dataset
    # registry for details and troubleshooting.
    dataset_registry_url = REGISTRY_BASE_URL + "/" + gbif_dataset_uuid
    print(
        "Initiating crawl for EDI dataset '"
        + local_dataset_id
        + "' / GBIF dataset '"
        + gbif_dataset_uuid
        + "'. See GBIF Registry "
        + "for details:\n"
        + dataset_registry_url
    )

    # Clear the list of local endpoints so when the endpoint is added below,
    # it will result in only one being listed on the GBIF dataset landing page.
    # Multiple listings could be confusing to end users.
    delete_local_dataset_endpoints(gbif_dataset_uuid)

    # Post the local dataset endpoint to GBIF. This will initiate a crawl of
    # the local dataset landing page metadata on the first post but not on
    # subsequent posts (updates).
    post_local_dataset_endpoint(local_dataset_endpoint, gbif_dataset_uuid)

    # Post a new metadata document to update the GBIF landing page. This is
    # necessary because GBIF doesn't "re-crawl" the local dataset metadata when
    # the new local dataset endpoint is updated.
    if has_metadata(gbif_dataset_uuid):
        post_new_metadata_document(local_dataset_id, gbif_dataset_uuid)


def post_new_metadata_document(local_dataset_id, gbif_dataset_uuid):
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
    """
    metadata = read_local_dataset_metadata(local_dataset_id)
    resp = post(
        GBIF_API + "/" + gbif_dataset_uuid + "/document",
        data=metadata,
        auth=(USER_NAME, PASSWORD),
        headers={"Content-Type": "application/xml"},
        timeout=60,
    )
    resp.raise_for_status()


def post_local_dataset_endpoint(local_dataset_endpoint, gbif_dataset_uuid):
    """Post a local dataset endpoint to GBIF.

    Parameters
    ----------
    local_dataset_endpoint : str
        This is the URL for downloading the dataset (.zip archive) at the EDI
        repository. Use the get_local_dataset_endpoint function in the
        utilities module to obtain this value.
        gbif_dataset_uuid : str
        The registration identifier assigned by GBIF to the local dataset
        group.

    Returns
    -------
    None
        Will raise an exception if the POST fails."""
    my_endpoint = {"url": local_dataset_endpoint, "type": "DWC_ARCHIVE"}
    resp = post(
        GBIF_API + "/" + gbif_dataset_uuid + "/endpoint",
        data=json.dumps(my_endpoint),
        auth=(USER_NAME, PASSWORD),
        headers={"Content-Type": "application/json"},
        timeout=60,
    )
    resp.raise_for_status()


def delete_local_dataset_endpoints(gbif_dataset_uuid):
    """Delete all local dataset endpoints from a GBIF dataset.

    Parameters
    ----------
    gbif_dataset_uuid : str
        The registration identifier assigned by GBIF to the local dataset.

    Returns
    -------
    None
        Will raise an exception if the DELETE fails.
    """
    # Get the list of existing endpoints to delete
    endpoints = get(
        GBIF_API + "/" + gbif_dataset_uuid + "/endpoint",
        auth=(USER_NAME, PASSWORD),
        headers={"Content-Type": "application/json"},
        timeout=60,
    )
    endpoints.raise_for_status()

    # Delete each endpoint
    if len(endpoints.json()) != 0:
        for item in endpoints.json():
            key = item.get("key")
            resp = delete(
                GBIF_API + "/" + gbif_dataset_uuid + "/endpoint/" + str(key),
                auth=(USER_NAME, PASSWORD),
                headers={"Content-Type": "application/json"},
                timeout=60,
            )
            resp.raise_for_status()
