"""Functions for calling a GBIF crawl."""

import json
from requests import post, get, delete
from gbif_registrar.config import username, password, gbif_api, registry_header
from gbif_registrar.utilities import read_local_dataset_metadata


def initiate_crawl(local_dataset_endpoint, gbif_dataset_uuid, local_dataset_id):
    """Initiate a crawl for a dataset at GBIF.

    Parameters
    ----------
    local_dataset_endpoint : str
        This is the URL for downloading the dataset (.zip archive) at the EDI
        repository. It has the format: https://pasta.lternet.edu/package/
        download/eml/{scope}/{identifier}/{revision}.
    gbif_dataset_uuid : str
        The registration identifier assigned by GBIF to the local dataset
        group.
    local_dataset_id : str
        The identifier of the dataset in the EDI repository. Has the format:
        {scope}.{identifier}.{revision}.

    Returns
    -------
    None
        The registrations file as a .csv.
    """
    # Notify user of the dataset being crawled and provide link to the dataset
    # registry for details and troubleshooting.
    dataset_registry_url = registry_header + "/" + gbif_dataset_uuid
    print("Initiating crawl for EDI dataset '" + local_dataset_id +
          "' / GBIF dataset '" + gbif_dataset_uuid + "'. See GBIF Registry " +
          "for details:\n" + dataset_registry_url)

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
    # TODO: Call if is an update, not a new dataset?
    post_new_metadata_document(gbif_dataset_uuid, local_dataset_id)

    # TODO: Add datetime to log if successful.
    return None


def post_new_metadata_document(gbif_dataset_uuid, local_dataset_id):
    """Post a new metadata document to GBIF.

    Parameters
    ----------
    gbif_dataset_uuid : str
        The registration identifier assigned by GBIF to the local dataset
        group.
    local_dataset_id : str
        The identifier of the dataset in the EDI repository. Has the format:
        {scope}.{identifier}.{revision}.

    Returns
    -------
    None
        Will raise an exception if the POST fails.
    """
    metadata = read_local_dataset_metadata(local_dataset_id)
    resp = post(
        gbif_api + "/" + gbif_dataset_uuid + "/document",
        data=metadata,
        auth=(username, password),
        headers={'Content-Type': 'application/xml'}
    )
    resp.raise_for_status()
    return None


def post_local_dataset_endpoint(local_dataset_endpoint, gbif_dataset_uuid):
    """Post a local dataset endpoint to GBIF.

    Parameters
    ----------
    local_dataset_endpoint : str
        This is the URL for downloading the dataset (.zip archive) at the EDI
        repository. It has the format: https://pasta.lternet.edu/package/
        download/eml/{scope}/{identifier}/{revision}.
        gbif_dataset_uuid : str
        The registration identifier assigned by GBIF to the local dataset
        group.

    Returns
    -------
    None
        Will raise an exception if the POST fails."""
    my_endpoint = {"url": local_dataset_endpoint, "type": "DWC_ARCHIVE"}
    resp = post(
        gbif_api + "/" + gbif_dataset_uuid + "/endpoint",
        data=json.dumps(my_endpoint),
        auth=(username, password),
        headers={'Content-Type': 'application/json'}
    )
    resp.raise_for_status()
    # TODO: Add datetime to log if successful.
    return None


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
        gbif_api + "/" + gbif_dataset_uuid + "/endpoint",
        auth=(username, password),
        headers={'Content-Type': 'application/json'}
    )
    endpoints.raise_for_status()

    # Delete each endpoint
    if len(endpoints.json()) != 0:
        for item in endpoints.json():
            key = item.get("key")
            resp = delete(
                gbif_api + "/" + gbif_dataset_uuid + "/endpoint/" + str(key),
                auth=(username, password),
                headers={'Content-Type': 'application/json'}
            )
            resp.raise_for_status()
    return None
