# CHANGELOG



## v0.2.0 (2024-01-17)

### Build

* build: remove dev dependencies to lighten package

Remove developer dependencies from the list of user/production
dependencies to lighten the installation process for users. ([`5496256`](https://github.com/EDIorg/gbif_registrar/commit/5496256537c3786557d8b7be0379c56ecb6c7b40))

### Ci

* ci: allow GHA to bypass protection rules on release

Permit GitHub Actions to bypass repository branch protection rules to
enable Python Semantic Release to commit release-related changes back
to the main branch. ([`d3c012b`](https://github.com/EDIorg/gbif_registrar/commit/d3c012b31055d0bd8a0259d5eccb8121f0b52c59))

* ci: fix failing release workflow

Update the failing release workflow (GitHub Action) to enable Python
Semantic Release to automatically create a new release when the
development branch is merged into main.

- Add the GITHUB_TOKEN to the semantic release step, where it is
necessary for committing changes, using the standard syntax for
referencing secrets.
- Include the missing versioning command in the semantic release step to
ensure the new version is calculated.
- Correct the outdated syntax for referencing the version number in the
pyproject.toml file to align with the requirements of the current version
of Python Semantic Release. ([`49c986f`](https://github.com/EDIorg/gbif_registrar/commit/49c986f324a1838bdb6df1d03e3b56b8cf6140cf))

* ci: update release token reference

Update the name of the authentication token used by the CD GitHub
Actions Workflow to reflect the new permissive permissions set on the
default repository token, resolving the CD workflow failure. ([`dc80841`](https://github.com/EDIorg/gbif_registrar/commit/dc80841d49b089630c10fbab143f725f63d262a2))

* ci: update failing GitHub Action workflows

Adjust failing GitHub Actions workflows for &#39;checkout&#39; and
 &#39;setup-python&#39; used in the CD workflow. This workflow differs from the
CI workflow in that authentication is required for git commit and
merging operations. ([`bf30458`](https://github.com/EDIorg/gbif_registrar/commit/bf304581a902ad4f2bbfe0983924ea57c5aaf9b7))

* ci: ignore pylint c-extension-no-member messages

Ignore pylint &#39;c-extension-no-member&#39; (I1101) messages, originating
from lxml, for the sake of a readable message log.

Another option, adding lxml to the pylint --extension-pkg-allow-list,
may run arbitrary code and is a decision that shouldn&#39;t be made for
collaborators running pylint in the context of this project. ([`3b9cefb`](https://github.com/EDIorg/gbif_registrar/commit/3b9cefbc509f0cca75d612b40fab072190c948ba))

* ci: update GitHub Actions

Assign GitHub Actions branch merge permissions to ensure that
&#39;development&#39; remains up-to-date with the main branch after &#39;main&#39;
is tagged during the release process.

Declare Pylint checks in &#39;pyproject.toml&#39; to ensure synchronization
between local checks and CI pipeline checks. ([`19e784f`](https://github.com/EDIorg/gbif_registrar/commit/19e784fd352a4b720bc57586a9087c47d7697ef2))

### Documentation

* docs: add blank space for release commit

Insert an empty blank space into the README to ease the creation of a
commit message, via Python Semantic Release, intended solely for bumping
the major version number.

BREAKING CHANGE: This marks the first fully functioning release of the
gbif_registrar package. The APIs of previously released functionality have
been considerably modified. ([`86b3da0`](https://github.com/EDIorg/gbif_registrar/commit/86b3da0226f6191c795728a9df53a297627da823))

* docs: update CONTRIBUTING for current project status

Revise the CONTRIBUTING file to align with the current status of the project. ([`71e6380`](https://github.com/EDIorg/gbif_registrar/commit/71e6380be2e7436760710ac343e6f345536f75a5))

* docs: emphasize running main workflow after creation

Emphasize the importance of running the main workflow after creation,
as skipping this step can result in incomplete registration and uploading
of a package to GBIF. ([`20d937e`](https://github.com/EDIorg/gbif_registrar/commit/20d937ed2d10f0edd11d09d6318ca108342a6e86))

* docs: update installation instructions

Revise installation instructions to recommend using pip from GitHub
rather than conda. While installation from conda is possible, the pip
method is more straightforward. ([`49d3ffa`](https://github.com/EDIorg/gbif_registrar/commit/49d3ffaf928a3fef3dc086e477cbb78788ada79f))

* docs: add examples of public-facing API usage

Add missing examples of public-facing API usage to provide users with
demonstrations of how to use the functions. ([`85f5364`](https://github.com/EDIorg/gbif_registrar/commit/85f53647e212be79672bb0cddff89a013ce52149))

* docs: encourage subscription to API mailing list

Add a note to the developer section of the README, advising maintainers
to subscribe to the EDI and GBIF API mailing lists for timely updates on
outages and changes. This ensures they can adjust expectations or the
codebase accordingly. ([`d62edb6`](https://github.com/EDIorg/gbif_registrar/commit/d62edb6ac84aab19acf8fb5c60498a62971c72bd))

* docs: correct subsection formatting

Apply a small fix to ensure consistent subsection formatting throughout the
document. ([`71a837e`](https://github.com/EDIorg/gbif_registrar/commit/71a837e7ce5ef4848d0263dae9695bd07225ecb0))

* docs: clarify dataset synchronization concept

Enhance clarity in the documentation regarding the concept of dataset
synchronization to preempt any potential confusion. ([`1ba25e7`](https://github.com/EDIorg/gbif_registrar/commit/1ba25e7b8a1f69785719b9df76fff952bfd91d3f))

* docs: update README for release

Add major missing components to the README in preparation for release. ([`e55cccf`](https://github.com/EDIorg/gbif_registrar/commit/e55cccf6d16e3d26700e05213360c0cde167a8c1))

* docs: standardize descriptions for a consistent API

Standardize function descriptions for API clarity and consistency. ([`947093b`](https://github.com/EDIorg/gbif_registrar/commit/947093b180e4403ab46b2d7550dce114e61da10c))

* docs: standardize parameters for consistent API

Standardize function parameter names and definitions for a consistent public
facing API. ([`92a56ec`](https://github.com/EDIorg/gbif_registrar/commit/92a56ec0d8cfc6e0e82db04752403ae266820908))

* docs: comment for clarity and understanding

Update code and test comments for improved clarity and understanding. ([`88842cb`](https://github.com/EDIorg/gbif_registrar/commit/88842cb78a47c956606ef4f8a6e029f818041bd1))

* docs: revise descriptions of a few utilities

Enhance descriptions and provide examples for the utility functions
&#39;get_local_dataset_group_id,&#39; &#39;get_local_dataset_endpoint,&#39; and
&#39;get_gbif_dataset_uuid&#39; to facilitate better understanding. ([`eae5990`](https://github.com/EDIorg/gbif_registrar/commit/eae5990eee6dd838e7fb2a6575defd95fda00bc7))

* docs: fix outdated references to read_registrations

Address outdated mentions of the &#39;read_registrations&#39; function that were
missed in commit 39367cc76f73aaa2159c627be37c0c4a508b4472. ([`37745d6`](https://github.com/EDIorg/gbif_registrar/commit/37745d646272d34b476c7ebda40e0e106b07d91e))

* docs: address RTD build deprecation

Switch to &#39;build.os&#39; instead of &#39;build.image&#39; to address the deprecation
of the &#39;build.image&#39; config key in Read the Docs. This change is
necessary for successful documentation building. ([`85e3fde`](https://github.com/EDIorg/gbif_registrar/commit/85e3fde67a99d0ec30bce8633218bc93ad31504b))

### Feature

* feat: upload new and revised datasets to GBIF

Implement a new function for uploading both new and revised datasets to
GBIF. Build the workflow to handle typical conditions and edge cases.
Additionally, create integration tests for making actual HTTP calls,
extended tests meant for occasional manual execution, and mock HTTP
calls, which are always run and provide faster results. ([`53219b6`](https://github.com/EDIorg/gbif_registrar/commit/53219b6563f768ac4cef77789d1ca797d43b5ca4))

* feat: enable registration repair on demand

Modify &#39;complete_registration_records&#39; to operate on a single record
when directed to do so, rather than always processing all incomplete
registrations. ([`e164d13`](https://github.com/EDIorg/gbif_registrar/commit/e164d136231548e880223b616a90eda159c5eef7))

* feat: check synchronization of local dataset w/GBIF

Report the success or failure of a dataset creation or update operation
to alert users of synchronization issues. Define success and failure by
comparing the publication date of the local dataset EML metadata
and the endpoint of the zip archive download, with that of the remote
GBIF instance.

Move get_local_dataset_endpoint to utilities.py to prevent a circular
reference. ([`c9ebad3`](https://github.com/EDIorg/gbif_registrar/commit/c9ebad36bcacdc1351e171092f30cae06f13c035))

* feat: wrap get GBIF dataset details for general use

Wrap calls for GBIF dataset details to simplify response handling and
to be DRY when calling from different contexts. ([`c3ec165`](https://github.com/EDIorg/gbif_registrar/commit/c3ec165e52e43561133b1a942f54d9a135db8167))

* feat: post local datasets to GBIF

Publish a set of functions for posting a local dataset to GBIF and 
maintaining synchronization as the local dataset evolves over time. ([`14336ac`](https://github.com/EDIorg/gbif_registrar/commit/14336ac7de5c52d37d9452e4d746695111c820c6))

### Fix

* fix: resolve reference to dataset group, not endpoint

To retrieve the corresponding &#39;gbif_dataset_uuid&#39; without errors,
utilize the &#39;local_dataset_group_id&#39; instead of the
&#39;local_dataset_endpoint.&#39; The &#39;local_dataset_endpoint&#39; does not
reference previously used gbif_dataset_uuid values due to its
one-to-one cardinality. ([`5139a62`](https://github.com/EDIorg/gbif_registrar/commit/5139a62d1d7b49bcdf9a7e53c884e5680cf53141))

* fix: update dependencies to resolve doc build failures

Update the &#39;autoapi.extension&#39; to prevent the exception &#34;&#39;Module&#39; object 
has no attribute &#39;doc&#39;&#34; and to enable successful local and Read the Docs 
documentation builds.

Pin project documentation dependencies to address the deprecation of 
default project dependencies on Read the Docs (see: https://blog.readthedocs.com/newsletter-september-2023/).

Update related project dependencies and resolve associated deprecation 
errors and warnings to maintain a functional code base. ([`f23fc23`](https://github.com/EDIorg/gbif_registrar/commit/f23fc2386f3f80a7100c696d8b620392b2ed260f))

* fix: use PASTA environment consistently

Use the PASTA_ENVIRONMENT variable to ensure consistent alignment of
data package references. Using different environments results in data package
reference mismatches and various errors throughout the application code. ([`2370ab0`](https://github.com/EDIorg/gbif_registrar/commit/2370ab03f516b3cd2c2c2638af9050376e5c2639))

* fix: use synchronized dataset for testing

Add a dataset that has been synchronized between EDI and GBIF to
&#39;registrations.csv&#39; for testing purposes. ([`cc30d49`](https://github.com/EDIorg/gbif_registrar/commit/cc30d49b1d5c16e5875fc3365c637b90c10b285a))

* fix: get new uuid if it does not exist

Fix the logic in &#39;get_gbif_dataset_uuid&#39; for determining an empty gbif_dataset_uuid to ensure a new value is requested if it doesn&#39;t yet exist.

Additionally, use pytest-mock to simulate both success and failure conditions for this feature. ([`1095985`](https://github.com/EDIorg/gbif_registrar/commit/1095985a509edaa55451419043ea087cd4734de3))

* fix: address pylint messages

Address lingering pylint messages to adhere to best practices and clean
up the message log, which has become quite lengthy. ([`c9ab920`](https://github.com/EDIorg/gbif_registrar/commit/c9ab920de36a8adad08fbbdd78fbdd929096b820))

* fix: update outdated dependency files

Update the outdated dependency files to build the project without error. ([`fa4d11c`](https://github.com/EDIorg/gbif_registrar/commit/fa4d11cbe130c204c5fbddebccc5e8a8b5286783))

### Refactor

* refactor: rename module for improved descriptiveness

Rename the &#39;crawl.py&#39; module to &#39;upload.py&#39; to better reflect its
purpose, which involves the user posting content to GBIF rather
than performing crawling operations. ([`50205d6`](https://github.com/EDIorg/gbif_registrar/commit/50205d6b74dfea839980140b0297879344e621fd))

* refactor: enhance credential security in config file

- Relocate the configuration file to an external location, removing it from version control to ensure the safety of credentials.
- Introduce a &#39;write configuration file&#39; helper function, which generates a boilerplate configuration to be completed by the user.
- Create utility functions for loading and unloading the configuration as environmental variables, making them accessible throughout the package.
- Note: The current implementation doesn&#39;t fully restore the user&#39;s environmental variables to their original state, as any variables with the same names will be overwritten by the load_configuration function and removed by the unload_configuration function. Addressing this issue is a potential improvement for future implementation. ([`dfa5e39`](https://github.com/EDIorg/gbif_registrar/commit/dfa5e39c9994075eba50354b41aea097a168e9ce))

* refactor: expand abbreviations for clarity

Expand abbreviated references to the registrations data frame for
improved clarity and comprehension ([`9ea61b1`](https://github.com/EDIorg/gbif_registrar/commit/9ea61b1f4f338b347328906b0d942680189cde5d))

* refactor: eliminate useless &#39;_has_metadata&#39; function

Remove the &#39;_has_metadata&#39; function as it does not serve a purpose.
Initially, it was designed to determine whether a local dataset group
had a member on GBIF and was used to guide decision logic concerning
resetting dataset endpoints and re-uploading metadata in the event of a
dataset update. However, it became apparent that this function returned
 &#39;True&#39; even if only boilerplate stand-in metadata was posted to GBIF
before the actual metadata was posted during a crawl operation. ([`bff89ba`](https://github.com/EDIorg/gbif_registrar/commit/bff89bae7f8f0fd3cfdf25a96edde2a05def29a6))

* refactor: check for &#39;NA&#39; instead of &#39;None&#39;

When performing decision logic (boolean operations) based on values
retrieved from the registrations file, ensure that the values are &#39;NA&#39;
rather than &#39;None.&#39; This change is necessary to avoid the &#39;boolean value
of NA is ambiguous&#39; error potentially arising from the recent
implementation at commit
f23fc2386f3f80a7100c696d8b620392b2ed260f, which transitions from
using &#39;None&#39; to &#39;NA&#39; values in the registrations file in preparation for
addressing a future deprecation in pandas. ([`4b213cf`](https://github.com/EDIorg/gbif_registrar/commit/4b213cf6947cca72854b0c07e39eadc8f5b9cf72))

* refactor: clarify definition of &#39;synchronization&#39;

Rename the &#39;is_synchronized&#39; column to &#39;synchronized&#39; to clarify its
meaning, shifting from &#34;this dataset is currently synchronized with
GBIF&#34; to &#34;this dataset has in the past been synchronized with GBIF.&#34;
Also, updated the &#39;check_is_synchronized&#39; function to align with this
renaming. ([`2cb5392`](https://github.com/EDIorg/gbif_registrar/commit/2cb539209b35f22651c5a689b77de4e97912b1ac))

* refactor: internalize utilities for backwards compatibility

Internalize utility functions to reduce the risk of introducing
backward compatibility issues in the public-facing API when
refactoring the codebase. ([`6a71eec`](https://github.com/EDIorg/gbif_registrar/commit/6a71eecb8e13df926a19528b41bdfad8b9b13cff))

* refactor: default synchronization value to &#39;False&#39;

Change the default synchronization indicator from &#39;None&#39; to &#39;False&#39; to
align the code with example and test usage. ([`aa6353b`](https://github.com/EDIorg/gbif_registrar/commit/aa6353b2851ca89656684dd375655b27772bb45d))

* refactor: deprecate extended validation checks

Enforce consistent validation of registration file contents using
extended checks, always. Remove the controlling parameter for this
half-implemented external repository customization feature, which we
have decided not to support. ([`e5be3d9`](https://github.com/EDIorg/gbif_registrar/commit/e5be3d9fcc7977f31d382c7d7244f467c3395d04))

* refactor: separate concerns of register_dataset

Refactor &#39;register_dataset&#39; to exclusively handle the registration of a
single dataset, removing the attempt to repair partially registered
datasets resulting from past registration failures. Move the repair
action to &#39;complete_registration_records&#39;. This separation of
concerns improves code maintainability and usability. ([`12742f4`](https://github.com/EDIorg/gbif_registrar/commit/12742f4bfe03c5784b7c27386e85ccbbec5214bf))

* refactor: enhance clarity of complete_registrations

Rename the &#39;complete_registrations&#39; function and update documentation
to reflect that it handles the completion of all components within
registration records, not solely the &#39;gbif_dataset_uuid&#39;. ([`6266ef9`](https://github.com/EDIorg/gbif_registrar/commit/6266ef9cf53f65b3a3a8c92e2c44d746469bb299))

* refactor: enhance clarity in read_registrations

Rename the &#39;read_registrations&#39; function and the &#39;file_path&#39; parameter
to indicate that the registrations file is being read, and to follow a
consistent call pattern being implemented throughout the codebase. ([`39367cc`](https://github.com/EDIorg/gbif_registrar/commit/39367cc76f73aaa2159c627be37c0c4a508b4472))

* refactor: enhance clarity in the register function

- Rename the &#39;register&#39; function to explicitly indicate that it
registers a dataset.
- Move the &#39;dataset&#39; parameter to the first position for improved
function call readability.
- Rename the &#39;file_path&#39; parameter to better convey that it represents
registration information as a file for better understanding. ([`c92b496`](https://github.com/EDIorg/gbif_registrar/commit/c92b4968a4cec4197412ec5345c35bf369a18acc))

* refactor: improve clarity in initialize_registrations

- Rename the &#39;initialize_registrations&#39; function to enhance understanding,
making it clear that it initializes a file.
- Enhance file content descriptions and their mappings to concepts in
the EDI repository for better comprehension.
- Move the function to the &#39;register.py&#39; module, where it joins similar
code for improved findability. ([`ee98c9e`](https://github.com/EDIorg/gbif_registrar/commit/ee98c9e9fd10cc1a8b499487aa408ddb77c9bb48))

* refactor: deprecate gbif_endpoint_set_datetime

Deprecate gbif_endpoint_set_datetime in favor of is_synchronized to
indicate the synchronization status of an EDI dataset with GBIF.

Is related to c9ebad36bcacdc1351e171092f30cae06f13c035. ([`2c7ea77`](https://github.com/EDIorg/gbif_registrar/commit/2c7ea77e6f55d9a34eb6882a72bb1108bc808f49))

* refactor: apply read_gbif_dataset_metadata

Apply &#39;read_gbif_dataset_metadata&#39; to functions requiring this
information in their custom implementations to maintain a DRY
codebase. ([`c5896e3`](https://github.com/EDIorg/gbif_registrar/commit/c5896e3ef63a5da3c0e04193c846a82cde8cc44f))

* refactor: rename get_gbif_datatset_details

Improve user understanding by renaming &#39;get_gbif_datatset_details.&#39;
Replace the &#39;get&#39; prefix with &#39;read&#39; to clarify the operation as an I/O
operation with possible parsing. ([`b1c4786`](https://github.com/EDIorg/gbif_registrar/commit/b1c4786e197faf57a9fc23c1174cc08a48438e7f))

* refactor: fail &#39;has_metadata&#39; gracefully

Handle HTTP errors gracefully in the &#39;has_metadata&#39; function to prevent
systematic failures.

Employ pytest-mock to simulate both success and failure conditions. ([`7381637`](https://github.com/EDIorg/gbif_registrar/commit/7381637cd3cee6629ab1921343c497c46e8f8754))

* refactor: fail &#39;read_local_dataset_metadata&#39; gracefully

Handle HTTP errors gracefully in the &#39;read_local_dataset_metadata&#39;
function to prevent systematic failures.

Employ pytest-mock to simulate both success and failure conditions. ([`a0e9515`](https://github.com/EDIorg/gbif_registrar/commit/a0e95151616ba740477eb123352726e75a3e3499))

* refactor: fail &#39;request_gbif_dataset_uuid&#39; gracefully

Handle HTTP errors gracefully in the &#39;request_gbif_dataset_uuid&#39;
function to prevent systematic failures. Employ pytest-mock to simulate
both success and failure conditions. ([`f1bca32`](https://github.com/EDIorg/gbif_registrar/commit/f1bca323448dbe4018bb31193825781a47c71a7f))

* refactor: check for metadata before replacing

Prior to replacement, verify the presence of a metadata document in
GBIF. This precaution prevents potential errors when attempting to
replace a metadata document that does not currently exist. ([`01ddd6c`](https://github.com/EDIorg/gbif_registrar/commit/01ddd6c1f5267749a314e74000495bcc98e79640))

* refactor: reorder func params for better semantics

Reorder the parameter positions of functions in the &#39;crawl&#39; module to
align function calls more effectively with the underlying semantics. ([`45f94c6`](https://github.com/EDIorg/gbif_registrar/commit/45f94c68de5b89e01604374f523b280348b95ac2))

### Test

* test: eliminate empty test module

Remove the empty &#39;test_validate.py&#39; module as testing for these routines
is consolidated in the &#39;test__utilities.py&#39; module. ([`4e11f80`](https://github.com/EDIorg/gbif_registrar/commit/4e11f803b15f8636af761aee2e270f75aedfafb6))

* test: verify reuse of &#39;gbif_dataset_uuid&#39; for updates

Confirm that the &#39;register_dataset&#39; function reuses the
 &#39;gbif_dataset_uuid&#39; for members sharing the same
&#39;local_dataset_group_id,&#39; enabling updates of the GBIF
dataset instance. ([`f7210e1`](https://github.com/EDIorg/gbif_registrar/commit/f7210e1641fdba3128780a2d97e9f85e4edb0072))

* test: register the first dataset w/o error

Test that the &#39;complete_registration_records&#39; function works for the
scenario of the first dataset to ensure that this situation does not
trigger an error. ([`3030cf9`](https://github.com/EDIorg/gbif_registrar/commit/3030cf98c490b800036bbae59f3f1473b242c55a))

* test: validate iterative registration repair

Executed &#39;complete_registration_records&#39; on a registrations file
containing two incomplete registrations to verify the functionality of
iterative registration repair under this specific use case. ([`07e2e67`](https://github.com/EDIorg/gbif_registrar/commit/07e2e67af97d32000f3320a02d21fc8964ab85e3))

* test: include missing test for failed registration

Add a test case to verify that a failed registration does not write a GBIF dataset UUID
in the registrations file, returns &#39;NA,&#39; and does not raise an exception. ([`e974ac9`](https://github.com/EDIorg/gbif_registrar/commit/e974ac9dea74d51eba0cb5d94aa9d1cbf1e9c279))

* test: share fixtures with conftest.py

Utilize &#39;conftest.py&#39; for sharing test fixtures, currently isolated
within test modules. ([`e067bae`](https://github.com/EDIorg/gbif_registrar/commit/e067baedd3c93be010699997e9c74f9fd20bd443))

* test: mock HTTP requests for &#39;register&#39;

Utilize pytest-mock to simulate both success and failure conditions for
the &#39;register&#39; function. ([`dabeec1`](https://github.com/EDIorg/gbif_registrar/commit/dabeec1602aa094a9748394f38bcbe8f2a2926f5))

* test: use pytest-mock to mock tests

Utilize pytest-mock to mock tests that involve remote API calls,
allowing tests to run even when offline. This approach enhances the
ability to thoroughly examine both pass and fail conditions. ([`4943677`](https://github.com/EDIorg/gbif_registrar/commit/49436778c8f7f5ed69c22e0dc632062c559182aa))


## v0.1.1 (2023-06-22)

### Build

* build: use Python 3.9 to fix readthedocs issue

When specifying Python 3.10 in .readthedocs.yml, an error is raised in
the build: &#39;AttributeError module types has no attribute UnionType&#39;. A
temporary fix to this issue is to use Python 3.9. While not optimal,
using 3.9 allows the current package docs to build, the conda
environment to resolve, and the package tests to pass.

This commit specifies Python 3.9 in .readthedocs.yml. ([`58d0960`](https://github.com/EDIorg/gbif_registrar/commit/58d0960faf3dfa0e283cfe351f0e7fe0c5853dfa))


## v0.1.0 (2023-06-22)

### Build

* build: update environment and requirements files ([`62cda52`](https://github.com/EDIorg/gbif_registrar/commit/62cda52150adc0583c3095efd8791db4201aa30f))

* build: update poetry lock ([`a5471ba`](https://github.com/EDIorg/gbif_registrar/commit/a5471ba036f7ed4537941a39052a6d6ce25056a7))

### Ci

* ci: format and lint PRs and merges ([`cd3b5c4`](https://github.com/EDIorg/gbif_registrar/commit/cd3b5c4ebc36f14dd3ac0c8b59def7d372903f56))

### Documentation

* docs: credit Margaret for authorship ([`05d8e27`](https://github.com/EDIorg/gbif_registrar/commit/05d8e2740d4ccd3bb02149bfb3d44da7ff70329f))

* docs: update contributing guidelines ([`12b94f4`](https://github.com/EDIorg/gbif_registrar/commit/12b94f4425694e978dd68bcce13c5afc448bfb04))

* docs: mention Pylint usage ([`f81b0ec`](https://github.com/EDIorg/gbif_registrar/commit/f81b0ec0ab966261533d965e275f62128d1303e2))

* docs: reformat project names ([`6ad14a8`](https://github.com/EDIorg/gbif_registrar/commit/6ad14a820b2f5063686170e98355aff19bfe2a7f))

* docs: Update contributing guidelines ([`41eb175`](https://github.com/EDIorg/gbif_registrar/commit/41eb1751b10cd91e2841049140bc2f9462fb9120))

### Feature

* feat: create function to register datasets w/GBIF ([`3cd7d14`](https://github.com/EDIorg/gbif_registrar/commit/3cd7d14e5876fd17f5071569e37e50585b3ad3ee))

* feat: extend registration checks

Closes #11 ([`d1b662e`](https://github.com/EDIorg/gbif_registrar/commit/d1b662ef0dfecbbb504253cc32ef350b8f95e97a))

* feat: validate registrations file

Closes #7 ([`2430c58`](https://github.com/EDIorg/gbif_registrar/commit/2430c58d71a7005d4f0beac00c27daeeda7a88c1))

* feat: read registrations file

Closes #8 ([`95de046`](https://github.com/EDIorg/gbif_registrar/commit/95de0461a59ea7e07118ed053b7833f5ffeeba00))

* feat: Initialize an empty registrations file

Closes #2 ([`73cd544`](https://github.com/EDIorg/gbif_registrar/commit/73cd5442b5b105b382157936445112eb7efd0ee7))

### Refactor

* refactor: format recent changes ([`40661c6`](https://github.com/EDIorg/gbif_registrar/commit/40661c6013bbb17aacd0f3ef31d75961fee58120))

* refactor: format and lint recent changes ([`15d71f4`](https://github.com/EDIorg/gbif_registrar/commit/15d71f4f164979738f428b30862fb1cb3633318b))

* refactor: rename a few things ([`92e6475`](https://github.com/EDIorg/gbif_registrar/commit/92e64759f864e446b39b3d5aae59d86e1339efb7))

### Test

* test: fix code formatting in test ([`4f70e00`](https://github.com/EDIorg/gbif_registrar/commit/4f70e000f05094621d79c3d4e19a2bacb02d49d2))

* test: add test/example registrations file

Closes #5 ([`2ae51b2`](https://github.com/EDIorg/gbif_registrar/commit/2ae51b25e047157f373b8a2de94ceaaedf57b195))

### Unknown

* Ignore sensitive data in config.py

The config.py file is used to store sensitive GBIF API client data and
should not be publicly exposed.

This commit adds the config.py file to .gitignore. ([`9fa6ae1`](https://github.com/EDIorg/gbif_registrar/commit/9fa6ae1dd4698c45d43cd5a248a26bee4a13a509))

* Run CI-CD actions on PR to main/dev branches ([`82a082a`](https://github.com/EDIorg/gbif_registrar/commit/82a082acdde5eae4d8c4113d6ded88c25c39d779))

* Note commit format requirements ([`39e1854`](https://github.com/EDIorg/gbif_registrar/commit/39e1854e0507bf7a831e59d2ba9c534141bbc428))

* First commit ([`487cf6a`](https://github.com/EDIorg/gbif_registrar/commit/487cf6aae865d192dffb51c8880be70676a2b9ea))
