"""Functions for calling a GBIF crawl."""
import requests
from gbif_registrar.config import username, password, gbif_api, registry_header
import json


def initiate_crawl(local_dataset_endpoint, gbif_dataset_uuid):

    # Get list of endpoints for dataset, /dataset/{UUID}/endpoint
    list_of_endpoints = requests.get(
        gbif_api + "/" + gbif_dataset_uuid + "/endpoint",
        auth=(username, password),
        headers={'Content-Type': 'application/json'}
    )

    # If list is not null then delete all endpoints for dataset otherwise multiple
    # endpoints will be listed, which we don't want.
    if len(list_of_endpoints.json()) != 0:
        for endpoint in list_of_endpoints.json():
            key = endpoint.get("key")
            delete_endpoint = requests.delete(
                gbif_api + "/" + gbif_dataset_uuid + "/endpoint/" + str(key),
                auth=(username, password),
                headers={'Content-Type': 'application/json'}
            )

    # Update datset at GBIF to initiate crawl (i.e. add endpoint)
    my_endpoint = {"url": local_dataset_endpoint, "type": "DWC_ARCHIVE"}
    update_dataset = requests.post(
        gbif_api + "/" + gbif_dataset_uuid + "/endpoint",
        data=json.dumps(my_endpoint),
        auth=(username, password),
        headers={'Content-Type': 'application/json'}
    )
    # TODO: Add datetime to log and assume it's OK

    if update_dataset.status_code != 201:
        # FIXME: Declare an exception for better message handling.
        # TODO: Create a registry log URL for the dataset. Add this value to the print statement.
        dataset_registry_url = registry_header + "/" + gbif_dataset_uuid
        print("Warning: GBIF dataset initiate crawl failed. Check the log.")

    # Add ingestion history?: https://registry.gbif-uat.org/dataset/b155a522-0992-46fa-a8f0-2306c98e6b79/ingestion-history


def post_metadata_document(gbif_dataset_uuid, local_dataset_endpoint):

    # Read metadata document from PASTA
    meta_request = requests.get(
        "https://pasta.lternet.edu/package/metadata/eml/edi/941/4"
    )

    # Post metadata document to GBIF
    my_endpoint = {"url": local_dataset_endpoint, "type": "DWC_ARCHIVE"}
    metadata = requests.post(
        gbif_api + "/" + gbif_dataset_uuid + "/document",
        data=json.dumps(my_endpoint),
        auth=(username, password),
        headers={'Content-Type': 'application/json'}
    )
