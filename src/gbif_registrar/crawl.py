"""Functions for calling a GBIF crawl."""

from time import sleep
from gbif_registrar._utilities import (
    _has_metadata,
    _post_new_metadata_document,
    _post_local_dataset_endpoint,
    _delete_local_dataset_endpoints,
    _read_registrations_file,
    _is_synchronized,
)
from gbif_registrar.config import (
    GBIF_DATASET_BASE_URL,
    REGISTRY_BASE_URL
)


def upload_dataset(local_dataset_id, registrations_file):
    """Upload a local dataset to GBIF.

    Parameters
    ----------
    local_dataset_id : str
        The identifier of the dataset in the EDI repository. Has the format:
        {scope}.{identifier}.{revision}.
    registrations_file : str
        The path to the registrations file.

    Returns
    -------
    None
        The registrations file as a .csv.

    Notes
    -----
    The synchronization status of the dataset is written to the registrations
    file. The status is True if the dataset was successfully synchronized with
    GBIF and False otherwise.
    """
    print(f"Uploading {local_dataset_id} to GBIF.")

    # Read the registrations file to obtain relevant information for the upload
    # process.
    with open(registrations_file, "r", encoding="utf-8") as registrations:
        registrations = _read_registrations_file(registrations_file)

    # Stop if not registered
    if local_dataset_id not in registrations["local_dataset_id"].values:
        print("The local dataset ID is not in the registrations file. "
              "Registration is required first.")
        return None

    # Obtain relevant information for the upload process from the registrations
    gbif_dataset_uuid = registrations[local_dataset_id]["gbif_dataset_uuid"]
    local_dataset_endpoint = registrations[local_dataset_id]["local_dataset_endpoint"]
    local_dataset_group_id = registrations[local_dataset_id]["local_dataset_group_id"]
    synchronized = registrations[local_dataset_id]["synchronized"]

    # Determine if the local dataset belongs to a local data group that is
    # already on GBIF. Do this to inform the decision logic below.
    has_metadata = _has_metadata(gbif_dataset_uuid)
    if has_metadata:
        print(
            f"The {local_dataset_group_id} dataset group exists on GBIF."
        )
    else:
        print(
            f"The {local_dataset_group_id} dataset group does not exist on "
            f"GBIF"
        )

    # Check if the local_dataset_id is already synchronized with GBIF and stop
    # the upload process if it is.
    if synchronized:
        print(
            f"{local_dataset_id} is already synchronized with GBIF. Skipping"
            f" the upload process."
        )
        # Write the synchronization status to the registrations file to handle
        # the case of a successful upload but timed out synchronization
        # check, which would result in the status being False in the
        # registrations file.
        if registrations[local_dataset_id]["synchronized"] is False:
            registrations[local_dataset_id]["synchronized"] = True
            registrations.to_csv(registrations_file, index=False, mode="w")
            print(
                f"Updated the registrations file with the new synchronization "
                f"status of {local_dataset_id}."
            )
        return None

    # Clear the list of local endpoints so when the endpoint is added below,
    # it will result in only one being listed on the GBIF dataset landing page.
    # Multiple listings could be confusing to end users.
    if has_metadata:
        _delete_local_dataset_endpoints(gbif_dataset_uuid)
        print(
            f"Deleted existing local dataset endpoints to make space for "
            f"the new {local_dataset_id} endpoint."
        )

    # Post the local dataset endpoint to GBIF. This will initiate a crawl of
    # the local dataset landing page metadata on the first post but not on
    # subsequent posts (updates). In the latter case, the local dataset
    # landing page metadata will also need to be posted to update the GBIF
    # landing page.
    _post_local_dataset_endpoint(local_dataset_endpoint, gbif_dataset_uuid)
    print(f"Posted local dataset endpoint {local_dataset_endpoint} to GBIF.")

    # For revised datasets, post a new metadata document to update the GBIF
    # landing page. This is necessary because GBIF doesn't "re-crawl" the
    # local dataset metadata when the new local dataset endpoint is updated.
    if has_metadata:
        _post_new_metadata_document(local_dataset_id, gbif_dataset_uuid)
        print(f"Posted new metadata document for {local_dataset_id} to GBIF.")

    # TODO adjust max number of retries to the average synchronization time
    #  to increase chances of success while avoiding infinite loops. But also
    #  allow users to set the max number of retries for their system.
    # Run the is_synchronized function until a True value is returned or the
    # max number of attempts is reached.
    synchronized = False
    max_attempts = 1
    attempts = 0
    while not synchronized and attempts < max_attempts:
        sleep(1)
        print(f"Checking if {local_dataset_id} is synchronized with GBIF.")
        synchronized = _is_synchronized(local_dataset_id, registrations_file)
        attempts += 1

    if synchronized:  # Update the registrations file with the new status
        print(f"{local_dataset_id} is synchronized with GBIF.")
        with open(registrations_file, "r", encoding="utf-8") as registrations:
            registrations = _read_registrations_file(registrations_file)
        registrations[local_dataset_id]["synchronized"] = True
        registrations.to_csv(registrations_file, index=False, mode="w")
        print(
            f"Updated the registrations file with the new synchronization "
            f"status of {local_dataset_id}."
        )
        print(f"Upload of {local_dataset_id} to GBIF is complete!")
        print("View the dataset on GBIF at:", GBIF_DATASET_BASE_URL + "/" +
              gbif_dataset_uuid)
    else:
        print(f"Checks on the synchronization status of {local_dataset_id} "
              f"with GBIF timed out. Please check back later.")
    print(f"For more information, see the GBIF log page for "
          f"{local_dataset_id}:", REGISTRY_BASE_URL + "/" + gbif_dataset_uuid)
    return None
