"""Functions for calling a GBIF crawl."""

from gbif_registrar.config import REGISTRY_BASE_URL
from gbif_registrar._utilities import (
    _has_metadata,
    _post_new_metadata_document,
    _post_local_dataset_endpoint,
    _delete_local_dataset_endpoints,
)


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
        _get_local_dataset_endpoint function in the utilities module.
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
    _delete_local_dataset_endpoints(gbif_dataset_uuid)

    # Post the local dataset endpoint to GBIF. This will initiate a crawl of
    # the local dataset landing page metadata on the first post but not on
    # subsequent posts (updates).
    _post_local_dataset_endpoint(local_dataset_endpoint, gbif_dataset_uuid)

    # Post a new metadata document to update the GBIF landing page. This is
    # necessary because GBIF doesn't "re-crawl" the local dataset metadata when
    # the new local dataset endpoint is updated.
    if _has_metadata(gbif_dataset_uuid):
        _post_new_metadata_document(local_dataset_id, gbif_dataset_uuid)
