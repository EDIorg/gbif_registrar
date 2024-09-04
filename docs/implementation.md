# implementation.md 

describes EDI's GBIF resistrar and how to work with it

initially, a diagram and table describing steps. 

## Overview

| Step | Who | Discription | 
| ------ | ---------- | ------------------------------------------------- |
| 1 | data submitter | upload L0 package | 
| 2 | EDI (or data submitter) | create L0 ecocomDP conversion script; create L1 pkg (include script); upload L1 package| 
| 2.1 | EDI and data submitter | determine if L0 is a candidate for GBIF submission | 
| 3 | EDI | Run DwC-A conversion script (create a L2 from L1) | 
| 4 | EDI | add L2 identifier to GBIF queue | 
| 5 | EDI | Create 3 PASTA event subscriptions | 
| 5.1 | EDI | Listener for new revision of L0 | 
| 5.2 | EDI | Listener for new revision of L1| 
| 5.3 | EDI | Listener for new revision of L2 | 
| 0 | EDI | TBD | 

![alt text](GBIF_process_setup2.svg)

## Guidelines for inclusion in the GBIF Registrar
Step 2.1 is a consultation between EDI and the data submitter (or representative) on whether the dataset is appropriate for GBIF. considerations inclucde 
- experimental data? probably not in GBIF (but a L1 may still be useful) 
- data that are already in GBIF (the data sumibtter is best equipped to recognize local data thay mabe already be in GBIF

## Automation

![alt text](GBIF_contributions_automated.svg)

### Failure Points
How are failures resolved? (e.g., a local script fails, gbif is down) how is progress tracked?
