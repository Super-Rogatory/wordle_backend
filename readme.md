# Microservice Implementation with FastAPI | Foreman | SQLite3

<!-- ABOUT THE PROJECT -->
## Contributors
- **Chukwudi Ikem**
- **James Talavera**


### Built With

* [FastAPI](https://fastapi.tiangolo.com/)
* [Foreman](https://pypi.org/project/foreman/)
* [SQLite](https://www.sqlite.org/index.html)
* [Uvicorn](https://www.uvicorn.org/)
* [Sqlite-Utils](https://pypi.org/project/sqlite-utils/)

<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Installation

* Make sure to have python3 and pip installed on your computer.
  ```sh
    sudo apt update
    sudo apt install --yes python3-pip ruby-foreman sqlite3 httpie
  ```

* Install FastAPI and other tools
  ```sh
    python3 -m pip install 'fastapi[all]' sqlite-utils uvicorn
  ```



### Final Steps

_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._

1. Clone the repo
   ```sh
   git clone https://github.com/Super-Rogatory/microservice_implementation
   ```
2. In the root directory of the app folder, create a .env and set values for CHECKING_PORT and VALIDATION_PORT.
    ```
    CHECKING_PORT=5000
    VALIDATION_PORT=5500
    ```
3. Run either the checkings or validation service (or both!)
   ```sh
   foreman start checkings
   foreman start validations
   ```
4. Travel to http://127.0.0.1:5000/docs or http://127.0.0.1:5500/docs (depends on the values inputted for CHECKING_PORT and VALIDATION_PORT)
5. Once there you can test out the routes!







