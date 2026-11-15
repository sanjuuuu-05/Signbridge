# check_duplicate_names.py
# Some camera file names (MVI_####.MOV) appear in more than one sign folder.
# This script hashes those files to see whether they are the SAME video filed
# under two signs (label problem) or DIFFERENT videos that share a camera number.
# Usage: python check_duplicate_names.py "subset_labels.csv" "DATA_FOLDER"
# Example: python check_duplicate_names.py "D:/Projects/Signbridge/ml/data/raw/subset_labels.csv" "D:/Projects/Signbridge/ml/data/raw"

import csv
import hashlib
import os
import sys

if len(sys.argv) < 3:
    print("Usage: python check_duplicate_names.py LABELS_CSV DATA_FOLDER")
    sys.exit(1)

labels_csv = sys.argv[1]
data_dir = sys.argv[2]

with open(labels_csv, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

by_name = {}
for row in rows:
    by_name.setdefault(row["original_name"], []).append(row)

same_content = 0
different_content = 0
missing = 0

for name in sorted(by_name):
    group = by_name[name]
    if len(group) < 2:
        continue

    hashes = []
    for row in group:
        path = os.path.join(data_dir, row["file"])
        if not os.path.exists(path):
            hashes.append("MISSING")
            missing += 1
            continue
        sha = hashlib.sha256()
        with open(path, "rb") as video:
            while True:
                chunk = video.read(1024 * 1024)
                if not chunk:
                    break
                sha.update(chunk)
        hashes.append(sha.hexdigest()[:12])

    if len(set(hashes)) == 1:
        verdict = "SAME CONTENT"
        same_content += 1
    else:
        verdict = "different"
        different_content += 1

    signs = [row["sign"] for row in group]
    print(name, "|", verdict, "|", signs, "|", hashes)

print()
print("names shared by 2+ signs:", same_content + different_content)
print("  same content (one video filed under two signs):", same_content)
print("  different content (same camera number, different videos):", different_content)
print("  files missing on disk:", missing)
