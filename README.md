# gbif_registrar

The `gbif_registrar` is a set of Python workflows designed for uploading [Environmental Data Initiative](https://edirepository.org/) (EDI) DwCA-Event core formatted datasets to the [Biodiversity Information Facility](https://www.gbif.org/) (GBIF). This enhances discovery and utilization of EDI data, contributing to improved biodiversity insights.

_Note, the term "dataset" used here is synonymous with "[data package](https://edirepository.org/resources/the-data-package)"._

## How it Works

The `gbif_registrar` operates through three steps:

1. **Register**: Associates an EDI dataset identifier with a GBIF group identifier and stores this information locally in a registrations file for future reference.
2. **Validate**: Runs a validation check on the registration file to ensure all necessary content is in place.
3. **Upload**: Initiates the upload of the newly registered dataset to GBIF.

For subsequent versions of an EDI dataset, the process repeats. The new version is added to the registrations file under the data package series GBIF group ID, undergoes validation for required content, and replaces the previous instance on GBIF.

## Getting Started
1. **Install**: The `gbif_registrar` may be installed from GitHub using pip: 

```bash
pip install git+https://github.com/EDIorg/gbif_registrar.git#egg=gbif_registrar
```
2. **Initialize Configuration**: Locally configure `gbif_registrar` to run on test or production environments and add credentials for authentication.
3. **Initialize Registration File**: Create a registration file to store information about EDI datasets on GBIF.
4. **Build the Main Workflow**: Develop the main.py workflow, outlining the major steps of the process. Below is an example of such a workflow:

```python
from gbif_registrar.configure import load_configuration, unload_configuration
from gbif_registrar.register import register_dataset
from gbif_registrar.validate import validate_registrations
from gbif_registrar.upload import upload_dataset


def main(local_dataset_id, registration_file, configuration_file):
    """Register a dataset and upload to GBIF.

    Parameters
    ----------
    local_dataset_id : str
        The identifier of a dataset in the EDI repository.
    registration_file : str
        Path of the registrations file.
    configuration_file : str
        Path of the configuration file.

    Returns
    -------
    None
        The registrations file written back to itself as a .csv, and containing
        the new registration record and synchronization status.

    Examples
    --------
    >>> main("edi.929.2", "registrations.csv", "configuration.json")
    """
    load_configuration(configuration_file)
    register_dataset(local_dataset_id, registration_file)
    validate_registrations(registration_file)
    upload_dataset(local_dataset_id, registration_file)
    unload_configuration()
```

5. **Run the Workflow**: Run the workflow from the command line, passing in the required arguments:

```python
main("edi.929.2", "registrations.csv", "configuration.json")
```

## Troubleshooting

If a registration fails:
1. Attempt to fix missing components by running the `complete_registration_records` function.
2. If the issue persists, manually diagnose the issue (see `gbif_registrar` messages) and edit the registrations file. 
3. Rerun the validation check to ensure completeness.

## Developer Notes
- To preserve acquired data and prevent duplication issues on GBIF, results are continuously written to the registration file.
- Integration tests that upload staged EDI datasets to the GBIF test server are run manually to save time in the development cycle and to respect GBIF storage space. To run the integration test, uncomment the "skip" marker on test_upload_dataset_real_requests in the test suite.
- The `gbif_registrar` wraps the [EDI](https://pastaplus-core.readthedocs.io/en/latest/doc_tree/pasta_api/index.html) and [GBIF](https://www.gbif.org/developer/registry) APIs. We therefore encourage maintainers of this package 
to subscribe to the [EDI PASTA GitHub repository](https://github.com/PASTAplus/PASTA) and the [GBIF API mailing list](https://lists.gbif.org/mailman/listinfo/api-users) for timely updates on outages and changes, so that the codebase can be updated accordingly.
 

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`gbif_registrar` was created by Colin Smith and Margaret O'Brien. It is licensed under the terms of the MIT license.

