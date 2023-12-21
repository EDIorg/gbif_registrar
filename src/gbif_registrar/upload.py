"""Functions for calling a GBIF crawl."""

from os import environ
from time import sleep
from gbif_registrar import _utilities


def upload_dataset(local_dataset_id, registrations_file):
    """Upload a local dataset to GBIF.

    Parameters
    ----------
    local_dataset_id : str
        The identifier of the dataset in the EDI repository. Has the format:
        {scope}.{identifier}.{revision}.
    registrations_file : str
        Path of the registrations file.

    Returns
    -------
    None
        The registrations file as a .csv.

    Notes
    -----
    The synchronization status of the dataset is written to the registrations
    file. The status is True if the dataset was successfully synchronized with
    GBIF and False otherwise.

    Print messages indicate the progress of the upload process. The messages
    are written to the standard output stream (stdout).

    This function requires authentication with GBIF. Use the load_configuration function
    from the authenticate module to do this.
    """
    print(f"Uploading {local_dataset_id} to GBIF.")

    # Read the registrations file to obtain information about the
    # local_dataset_id.
    with open(registrations_file, "r", encoding="utf-8") as registrations:
        registrations = _utilities._read_registrations_file(registrations_file)

    # A complete registration is required for this function to succeed. Stop
    # if this is not the case.
    if local_dataset_id not in registrations["local_dataset_id"].values:
        print(
            "The local dataset ID is not in the registrations file. "
            "Registration is required first."
        )
        return None

    # Assign registration info to variables for easy access in this function.
    index = registrations.index[
        registrations["local_dataset_id"] == local_dataset_id
    ].tolist()[0]
    local_dataset_endpoint = registrations.loc[index, "local_dataset_endpoint"]
    gbif_dataset_uuid = registrations.loc[index, "gbif_dataset_uuid"]
    synchronized = registrations.loc[index, "synchronized"]

    # Check if the local_dataset_id is already synchronized with GBIF and stop
    # if it is.
    if synchronized:
        print(
            f"{local_dataset_id} is already synchronized with GBIF. Skipping"
            f" the upload process."
        )
        return None

    # There is a latency in the initialization of a data package group on GBIF
    # that can result in the _is_synchronized function failing due to string
    # parsing errors. This case is unlikely to occur in contexts outside the
    # upload_dataset function, so we handle it here.
    try:
        synchronized = _utilities._is_synchronized(local_dataset_id, registrations_file)
    except AttributeError:
        synchronized = False
    if synchronized:
        # Handle the case of a successful upload but timed out synchronization
        # check, which would result in the status being False in the
        # registrations file.
        index = registrations.index[
            registrations["local_dataset_id"] == local_dataset_id
        ].tolist()[0]
        if not registrations.loc[index, "synchronized"]:
            registrations.loc[index, "synchronized"] = True
            registrations.to_csv(registrations_file, index=False, mode="w")
            print(
                f"Updated the registrations file with the missing "
                f"synchronization status of {local_dataset_id}."
            )
            return None

    # Clear the list of local endpoints so when the endpoint is added below,
    # it will result in only one being listed on the GBIF dataset landing page.
    # Multiple endpoint listings are confusing to end users.
    _utilities._delete_local_dataset_endpoints(gbif_dataset_uuid)
    print("Deleted local dataset endpoints from GBIF.")

    # Post the local dataset endpoint to GBIF. This will initiate a crawl of
    # the local dataset landing page metadata on the first post but not on
    # subsequent posts (the case of updated datasets). In the latter case, the
    # local dataset landing page metadata will also need to be posted to update
    # the GBIF landing page (below).
    _utilities._post_local_dataset_endpoint(local_dataset_endpoint, gbif_dataset_uuid)
    print(f"Posted local dataset endpoint {local_dataset_endpoint} to GBIF.")

    # For revised datasets, post a new metadata document in order to update
    # the GBIF landing page. This is necessary because GBIF doesn't "re-crawl"
    # the local dataset metadata when the new local dataset endpoint is
    # updated.
    _utilities._post_new_metadata_document(local_dataset_id, gbif_dataset_uuid)
    print(f"Posted new metadata document for {local_dataset_id} to GBIF.")

    # Run the is_synchronized function until a True value is returned or the
    # max number of attempts is reached.
    synchronized = False
    max_attempts = 12  # Average synchronization time is 20 seconds
    attempts = 0
    while not synchronized and attempts < max_attempts:
        print(f"Checking if {local_dataset_id} is synchronized with GBIF.")
        synchronized = _utilities._is_synchronized(local_dataset_id, registrations_file)
        attempts += 1
        sleep(5)

    # Update the registrations file with the new status
    if synchronized:
        print(f"{local_dataset_id} is synchronized with GBIF.")
        with open(registrations_file, "r", encoding="utf-8") as registrations:
            registrations = _utilities._read_registrations_file(registrations_file)
        registrations.loc[index, "synchronized"] = True
        registrations.to_csv(registrations_file, index=False, mode="w")
        print(
            f"Updated the registrations file with the new synchronization "
            f"status of {local_dataset_id}."
        )
        print(f"Upload of {local_dataset_id} to GBIF is complete.")
        print(
            "View the dataset on GBIF at:",
            environ["GBIF_DATASET_BASE_URL"] + "/" + gbif_dataset_uuid,
        )
    else:
        print(
            f"Checks on the synchronization status of {local_dataset_id} "
            f"with GBIF timed out. Please check the GBIF log page later."
            f"Once synchronization has occured, run "
            f"complete_registration_records function to reflect this "
            f"update."
        )
    print(
        f"For more information, see the GBIF log page for " f"{local_dataset_id}:",
        environ["REGISTRY_BASE_URL"] + "/" + gbif_dataset_uuid,
    )
    return None
