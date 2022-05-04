# Pick a Database Management System
###### _Note: You can use both at the same time._

### Sqlite (db)

SQLite provides a lightweight, disk-based relational database management system. SQLite3 allows the user to interface with SQLite databases in Python. In this folder lies functionality for all things SQL related. The standard bootstraping function exists within db_seed.sh.

## Features

- Use db_seed.sh to create sqlite databases (word_list.db, answers.db, etc) and shard the statistics database. 
- Utilize sqlite3 [name_of_db] command to open up the command line interface and interact with databases.
- Server Dependencies: checking_service.py, statistics_service.py, validation_service.py
