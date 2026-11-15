# make_subset.py
# Copies ALL videos of the 25 chosen signs from the INCLUDE dataset into one folder,
# one sub-folder per sign, and writes subset_labels.csv.
#
# Usage:
#   python make_subset.py "SOURCE_VIDEOS_FOLDER" "DESTINATION_FOLDER"
#
# Example:
#   python make_subset.py "D:/Projects/Indian Sign Language/dataset/videos" "D:/Projects/Signbridge/ml/data/raw"
#
# "Extra" folders are skipped (same choice as the 508-video count in the log).

import os
import re
import sys
import csv
import shutil

# (category folder name, sign name) - edit this list to change the vocabulary
vocabulary = [
    ("Greetings", "Hello"), ("Greetings", "Thank you"), ("Greetings", "How are you"),
    ("Greetings", "Good Morning"), ("Greetings", "Good night"),
    ("Places", "Hospital"), ("Places", "Bank"), ("Places", "School"),
    ("Places", "Restaurant"), ("Places", "Market"), ("Places", "Train Station"),
    ("People", "Mother"), ("People", "Father"), ("People", "Friend"),
    ("People", "Child"), ("People", "Woman"),
    ("Pronouns", "I"), ("Pronouns", "you"),
    ("Means_of_Transportation", "Bus"), ("Means_of_Transportation", "Car"),
    ("Means_of_Transportation", "Plane"),
    ("Colours", "Red"), ("Colours", "Green"),
    ("Animals", "Dog"), ("Animals", "Cat"),
]

if len(sys.argv) < 3:
    print("Usage: python make_subset.py SOURCE DESTINATION")
    sys.exit(1)

src = sys.argv[1]
dst = sys.argv[2]

if not os.path.isdir(src):
    print("Source is not a folder:", src)
    sys.exit(1)

os.makedirs(dst, exist_ok=True)

video_ext = (".mp4", ".mov", ".avi", ".mkv", ".webm")

# lowercase lookup so "Good Morning" matches "Good morning"
wanted = {}
for category, sign in vocabulary:
    wanted[(category.lower(), sign.lower())] = (category, sign)

rows = []
found_folders = {}          # (category, sign) -> list of source folders that matched
extra_counts = {}           # (category, sign) -> videos left behind in Extra folders

for folder, subfolders, filenames in os.walk(src):
    folder_name = os.path.basename(folder)
    parent_name = os.path.basename(os.path.dirname(folder))

    # Extra folder: its parent is the sign folder, the grandparent is the category
    if folder_name.lower() == "extra":
        sign_name = re.sub(r"^\S+\.\s+", "", parent_name)
        category_name = os.path.basename(os.path.dirname(os.path.dirname(folder)))
        key = (category_name.lower(), sign_name.lower())
        if key in wanted:
            n = len([f for f in filenames if f.lower().endswith(video_ext)])
            extra_counts[wanted[key]] = extra_counts.get(wanted[key], 0) + n
        continue

    # sign folder looks like "48. Hello"; category folder is its parent
    sign_name = re.sub(r"^\S+\.\s+", "", folder_name)
    key = (parent_name.lower(), sign_name.lower())
    if key not in wanted:
        continue

    category, sign = wanted[key]
    videos = sorted([f for f in filenames if f.lower().endswith(video_ext)])
    found_folders.setdefault((category, sign), []).append(folder)

    sign_dir = os.path.join(dst, sign.replace(" ", "_"))
    os.makedirs(sign_dir, exist_ok=True)

    for name in videos:
        source_path = os.path.join(folder, name)
        dest_path = os.path.join(sign_dir, name)
        shutil.copy2(source_path, dest_path)
        camera_number = int(re.search(r"(\d+)", name).group(1))
        rows.append([sign.replace(" ", "_") + "/" + name, category, sign, name,
                     camera_number, source_path])

csv_path = os.path.join(dst, "subset_labels.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["file", "category", "sign", "original_name", "camera_number", "source_path"])
    writer.writerows(rows)

# sanity checks
print("signs wanted:", len(vocabulary))
print("signs found :", len(found_folders))
for category, sign in vocabulary:
    if (category, sign) not in found_folders:
        print("  MISSING:", category, sign)
for key, folders in found_folders.items():
    if len(folders) > 1:
        print("  WARNING: more than one folder matched", key, folders)

print()
total_bytes = 0
for category, sign in vocabulary:
    count = len([r for r in rows if r[2] == sign and r[1] == category])
    extra = extra_counts.get((category, sign), 0)
    print(sign, "\t", count, "videos", "(Extra left behind:", extra, ")")

for r in rows:
    total_bytes += os.path.getsize(os.path.join(dst, r[0]))

print()
print("total videos copied:", len(rows))
print("size (MB):", round(total_bytes / (1024 * 1024), 1))
print("labels file:", csv_path)
