# RIFFSCOPE-INSIGHTS-PIPELINE documentation!

## Description

My first project such as data engineer

## Commands

The Makefile contains the central entry points for common tasks related to this project.

### Syncing data to cloud storage

* `make sync_data_up` will use `gsutil rsync` to recursively sync files in `data/` up to `gs://riffscope-raw/data/`.
* `make sync_data_down` will use `gsutil rsync` to recursively sync files in `gs://riffscope-raw/data/` to `data/`.


