#!/usr/bin/env python

import argparse
import hashlib
import os
import re
from tqdm import tqdm

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def main():
    parser = argparse.ArgumentParser(
        description='Find duplicate files (using md5 hash) and delete the duplicate using regex for selection.')
    parser.add_argument('folder', metavar='FOLDER', type=str, nargs='+',
                        help='the folder to check for duplicates')

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--dry-run', dest='dry', action='store_true',
                        default=False,
                        help='Do a dry run')

    rules = parser.add_argument_group("Selection options")
    rules.add_argument('--min-size', metavar='N', dest='min_size', type=int, default=-1,
                        help='Ignore files smaller than N')

    g = rules.add_mutually_exclusive_group()
    g.add_argument('--keep-oldest', dest='oldest', action='store_true',
                        default=False,
                        help='Keep the oldest file (default false, do not use date as comparison)')
    g.add_argument('--keep-newest', dest='newest', action='store_true',
                        default=False,
                        help='Keep the newest file (default false, do not use date as comparison)')
    rules.add_argument('--delete', dest='delete', type=str, nargs='*',
                        default=[],
                        help='List of regex to choose a file to delete')
    rules.add_argument('--keep', dest='keep', type=str, nargs='*',
                        default=[],
                        help='List of regex to choose a file to keep')
    args = parser.parse_args()
    dry = args.dry

    exp_d = [re.compile("copie|copy", re.IGNORECASE), re.compile("~$")]
    exp_k = []

    exp_d.extend(args.delete)
    exp_k.extend(args.keep)

    sizes = {}
    # Find all files with identical size
    n = 0
    for d in tqdm(args.folder,desc="Enumerating files..."):
            for i,(root, dir, files) in enumerate(os.walk(d)):

                n = n + 1
                for f in files:
                    path = root + os.sep + f
                    s = os.stat(path).st_size
                    if s < args.min_size:
                        continue
                    sizes.setdefault(s, []).append(path)

    # Find all files with identical hash
    same_files = []
    for files in tqdm(sizes.values(), desc="Computing hashes..."):
        thashs = {}
        for f in files:
            m = md5(f)
            thashs.setdefault(m, []).append(f)
        same_files.extend([f for f in thashs.values() if len(f) > 1])

    for files in same_files:
        files.sort(key=lambda f: os.path.getctime(f))
        if len(files) > 1:
            stop = False
            delete = set()
            keep = set()
            for (i, f) in enumerate(files):
                print("[%d] %s : date %d" % (i, f, os.path.getctime(f)))
                for red in exp_d:
                    if re.search(red, f):
                        delete.add(f)
                        break
                for rek in exp_k:
                    if re.search(rek, f):
                        keep.add(f)
                        break
                if stop:
                    break
            if len(keep) == 0 and len(delete) == 0:
                if args.oldest:
                    for i,f in enumerate(files[1:]):
                        delete.add(f)
                    print("Keeping only the oldest file %d" % (0))
                elif args.newest:
                    for i,f in enumerate(files[0:-1]):
                        delete.add(f)
                    print("Keeping only the newest file %d" % (len(files) - 1))
                else:
                    print("Not matching any expression... I don't know what to do !")
                    continue

            files = set(files)
            if len(files.difference(delete)) == 0:
                print("Not deleting because delete regex matched all files !")
                continue
            for f in delete:
                files.remove(f)
                keep.discard(f)
                print("Deleting %s (size %d)" % (f,os.stat(f).st_size))
                if not dry:
                    os.unlink(f)
            if len(files) <= 1:
                continue

            if len(keep) == 0:
                print("I still have files left but no keep regex...")
                continue

            delete = files.difference(keep)

            for f in delete:
                if not f in keep:
                    print("Deleting %s because it didn't match a keep expression" % f)
                    if not dry:
                        os.unlink(f)


if __name__ == '__main__':
    main()
