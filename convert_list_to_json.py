# Converting text to JSON.


import json
import sys

# using command-line argument to make code DRY
filename = f"{sys.argv[1]}"
in_file = filename + ".txt"
out_file = filename + ".json"
content = []  # initializing dictionary to be converted to JSON.
id = 1
# populates list of dictionaries
with open(in_file) as word_list:
    words = []  # will populate depending on cl-argument
    if filename == "answers":
        words = word_list.read().split(",")
    for word in words or word_list:
        obj = {}
        obj["id"] = id
        obj["name"] = "".join(ch for ch in word if ch.isalnum())
        content.append(obj)
        id = id + 1

# creating json file
out = open(out_file, "w")
json.dump(content, out, sort_keys=True)
out.close()
