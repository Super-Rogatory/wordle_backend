#!/bin/sh
# Chukwudi Ikem - should filter out the words file to a list of five-letter words (ignoring case) and outputing to word_list.txt (sorted).
# -E => extends regular expression containing both text and operator characters. -o print matches. -i ignore case
# iconv converts accent marked characters to their english counterpart so it's still usable.

grep -E -o "\<[a-z]{5}\>" /usr/share/dict/words | sort -u | iconv -f utf8 -t ascii//TRANSLIT//IGNORE  >> word_list.txt
if test `find "word_list.txt"`
then
    echo "Word_List File Created!"
fi

# make sure to install sqlite-utils -> pip install sqlite-utils
sqlite-utils create-database word_list.db 
sqlite-utils create-database answers.db

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# FOR WORD LIST
# run python file to convert word_list.txt to json file for database
python3 convert_list_to_json.py word_list
if test `find "word_list.json"`
then
    echo "Created JSON File for word_list - now deleting txt file."
fi

# at this point we should have a usable json file for the word list.
rm word_list.txt
# inserts all of the rows from our word_list.json into the table. 
sqlite-utils insert word_list.db words word_list.json --pk=id # sqlite3 word_list.db => SELECT * FROM words. to check out table.
rm word_list.json
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# FOR ANSWER LIST
curl --silent https://www.nytimes.com/games/wordle/main.bfba912f.js | sed -e 's/^.*var Ma=//' -e 's/,Oa=.*$//' -e 1q > answers.txt
python3 convert_list_to_json.py answers
if test `find "answers.json"`
then
    echo "Created JSON File for answers - now deleting txt file."
fi

# at this point we should have a usable json file for the answer list.
rm answers.txt


# same process as word_list
sqlite-utils insert answers.db answers answers.json --pk=id # sqlite3 answers.db => SELECT * FROM answers. to check out table
rm answers.json

# creates shard databases
sqlite-utils create-database stats_1.db
sqlite-utils create-database stats_2.db
sqlite-utils create-database stats_3.db
sqlite-utils create-database users.db

# get path for shard.py - so start_connection will work in shard.py
cd ../
python3 db/shard.py
