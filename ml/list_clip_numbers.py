# list_clip_numbers.py
# Prints the camera file numbers (MVI_####) in one sign folder, in order, with the gap
# to the previous file. Big gaps may mark a new recording session or a new signer.
# Usage: python list_clip_numbers.py "path/to/one/sign/folder"

import os
import re
import sys

if len(sys.argv) < 2:
    print("Usage: python list_clip_numbers.py FOLDER")
    print('Example: python list_clip_numbers.py "D:/Projects/Indian Sign Language/dataset/videos/Greetings_1of2/Greetings/48. Hello"')
    sys.exit(1)

folder = sys.argv[1]

if not os.path.isdir(folder):
    print("Not a folder:", folder)
    sys.exit(1)

names = sorted(f for f in os.listdir(folder) if f.upper().endswith(".MOV"))

previous = None
for name in names:
    match = re.search(r"(\d+)", name)
    number = int(match.group(1))
    if previous is None:
        gap = ""
    else:
        gap = number - previous
    print(name, "\t", "gap:", gap)
    previous = number

print("videos:", len(names))