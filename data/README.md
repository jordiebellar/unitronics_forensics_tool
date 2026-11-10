# data/

Everything the tool captures lives here. Git ignores this folder on purpose.

- runs/    new captures. One folder per run, named by the run script.
- legacy/  your old files from before the cleanup, sorted but not renamed.
  - _empty/            zero-byte files. Safe to delete.
  - _trash_pycache/    old Python cache. Safe to delete.

Data moves Pi -> PC with tools/sync_data.ps1. Back up anything you cannot recreate
(the flag0 and flag1 baseline dumps) to a second drive.
