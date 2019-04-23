# refdup
Find and delete duplicate files in a folder using regex


```
usage: refdup.py [-h] [--dry-run] [--delete [DELETE [DELETE ...]]]
                 [--keep [KEEP [KEEP ...]]]
                 FOLDER

Find duplicate files and delete the duplicate using regex for selection.

positional arguments:
  FOLDER                the folder to check for duplicates

optional arguments:
  -h, --help            show this help message and exit
  --dry-run             Do a dry run
  --delete [DELETE [DELETE ...]]
                        List of regex to choose a file to delete
  --keep [KEEP [KEEP ...]]
                        List of regex to choose a file to keep
```
