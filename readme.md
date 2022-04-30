# Microservice Implementation with FastAPI

<!-- ABOUT THE PROJECT -->
## Contributors
- **Chukwudi Ikem**
- **Madison Jordan**
- **James Talavera**
- **Farnam Keshavarzian**

### Built With

* [FastAPI](https://fastapi.tiangolo.com/)
* [Foreman](https://pypi.org/project/foreman/)
* [SQLite](https://www.sqlite.org/index.html)
* [Uvicorn](https://www.uvicorn.org/)
* [Sqlite-Utils](https://pypi.org/project/sqlite-utils/)
* [MultipleDispatch](https://pypi.org/project/multipledispatch/)

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Installation

* Make sure to have python3 and pip installed on your computer.
  ```sh
    sudo apt update
    sudo apt install --yes python3-pip ruby-foreman sqlite3 httpie
  ```

* Install FastAPI and other tools
  ```sh
    python3 -m pip install 'fastapi[all]' sqlite-utils uvicorn multipledispatch pydantic
  ```



### Final Steps

1. Clone the repo
   ```sh
   git clone https://github.com/Super-Rogatory/wordle_backend
   ```
2. In the root directory of the app folder, create a .env and set values for CHECKING_PORT and VALIDATION_PORT
    ```
    CHECKING_PORT=5000
    VALIDATION_PORT=5500
    ```
3. Seed the database! (you may need to change permissions on your local machine)
   ```sh
   cd db/
   ./db_seed.sh
   ```    
4. Run either the checkings or validation service (or both!)
   ```sh
   cd ../
   foreman start
   ```
5. Travel to http://127.0.0.1:9999/api/checkings/docs or http://127.0.0.1:9999/api/statistics/docs or http://127.0.0.1:9999/api/validations/docs (depends on the values inputted for which service you wish to test)
6. Once there you can test out the routes!







