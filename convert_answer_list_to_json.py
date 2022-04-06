# Converting text to JSON.


import json
import sys

print(sys.argv[1])
in_file = "answers.txt"
content = []  # initializing dictionary to be converted to JSON.
id = 1
# populates list of dictionaries
with open(in_file) as word_list:
    for word in word_list:
        obj = {}
        obj["id"] = id
        obj["name"] = word.strip()
        content.append(obj)
        id = id + 1

# creating json file
# out_file = open("answer.json", "w")
# json.dump(content, out_file, sort_keys=True)
# out_file.close()
