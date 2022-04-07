# Next Steps

- connect checking_service and validation_service to their respective databases.
- [x] Connect server to database to serve all words - testing to see if we can communicate between back-end services.
- [x] Checking if a guess is a valid five-letter word
- [ ] Adding and removing possible guesses

## Some Notes on Python SQLite Tutorial

- ### THE SETUP PROCESS
```
conn = sqlite3.connect('database.db')
c = conn.cursor()
```

- ### It's a two step process for retrieving data from a query. We must first execute the query, then we can use c.fetchall() | .fetchmany | fetchone() to get the results.
```
c.execute("SELECT * FROM words;")
print(c.fetchall())
```

- ### Remember to commit your changes
`conn.commit()`    