#!/bin/sh

#make db directory if it doesn't exist
mkdir -p db

# Chukwudi Ikem - should filter out the words file to a list of five-letter words (ignoring case) and outputing to word_list.txt (sorted).
# -E => extends regular expression containing both text and operator characters. -o print matches. -i ignore case
# iconv converts accent marked characters to their english counterpart so it's still usable.

grep -E -o "\<[a-z]{5}\>" /usr/share/dict/words | sort -u | iconv -f utf8 -t ascii//TRANSLIT//IGNORE  >> ./db/word_list.txt
if test `find "./db/word_list.txt"`
then
    echo "Word_List File Created!"
fi

# make sure to install sqlite-utils -> pip install sqlite-utils
sqlite-utils create-database ./db/word_list.db 
sqlite-utils create-database ./db/answers.db

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# FOR WORD LIST
# run python file to convert word_list.txt to json file for database
python3 ./bin/convert_list_to_json.py ./db/word_list
if test `find "./db/word_list.json"`
then
    echo "Created JSON File for word_list - now deleting txt file."
fi

# at this point we should have a usable json file for the word list.
rm ./db/word_list.txt
# inserts all of the rows from our word_list.json into the table. 
sqlite-utils insert ./db/word_list.db words ./db/word_list.json --pk=id # sqlite3 word_list.db => SELECT * FROM words. to check out table.
rm ./db/word_list.json
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# FOR ANSWER LIST
curl --silent https://www.nytimes.com/games/wordle/main.bfba912f.js | sed -e 's/^.*var Ma=//' -e 's/,Oa=.*$//' -e 1q > ./db/answers.txt
python3 ./bin/convert_list_to_json.py ./db/answers
if test `find "./db/answers.json"`
then
    echo "Created JSON File for answers - now deleting txt file."
fi

# at this point we should have a usable json file for the answer list.
rm ./db/answers.txt


# same process as word_list
sqlite-utils insert ./db/answers.db answers ./db/answers.json --pk=id # sqlite3 answers.db => SELECT * FROM answers. to check out table
rm ./db/answers.json



# build full statistics.db if it doesn't exist
if [ ! -f "./db/statistics.db" ]
then
    sqlite3 ./db/statistics.db < ./share/sqlite3-populated.sql
else
    echo "statistics.db already exists"
fi


# creates shard databases
sqlite-utils create-database ./db/stats_1.db
sqlite-utils create-database ./db/stats_2.db
sqlite-utils create-database ./db/stats_3.db
sqlite-utils create-database ./db/users.db

# get path for shard.py - so start_connection will work in shard.py
python3 bin/shard.py
