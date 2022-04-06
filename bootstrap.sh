#!/bin/sh
# Chukwudi Ikem - should filter out the words file to a list of five-letter words (ignoring case) and outputing to word_list.txt (sorted).
# -E => extends regular expression containing both text and operator characters. -o print matches. -i ignore case
# iconv converts accent marked characters to their english counterpart so it's still usable.

grep -E -o "\<[a-z]{5}\>" /usr/share/dict/words | sort -u | iconv -f utf8 -t ascii//TRANSLIT//IGNORE  >> word_list.txt
if test `find "word_list.txt"`
then
    echo "File Created!"
fi

# make sure to install sqlite-utils -> pip install sqlite-utils
sqlite-utils create-database word_list.db 
sqlite-utils create-database answers.db
# run python file to convert word_list.txt to json file for database
python3 convert_word_list_to_python.py
if test `find "word_list.json"`
then
    echo "Created JSON File - now deleting txt file."
fi
# at this point we should have a usable json file for the word list.
rm word_list.txt

# SQL statements to populate db | edit .txt to be a .csv file with a few modifications.
# sqlite-utils bulk chickens.db \
#   'insert into chickens (id, name) values (:id, :name)' \
#   chickens.csv --csv

# sqlite3 answers.db