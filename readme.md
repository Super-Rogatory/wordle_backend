# Microservice Implementation with FastAPI

<!-- ABOUT THE PROJECT -->

## Contributors

- **Chukwudi Ikem**
- **Madison Jordan**
- **Ryan Broguiere**


### Built With

- [FastAPI](https://fastapi.tiangolo.com/)
- [Foreman](https://pypi.org/project/foreman/)
- [SQLite](https://www.sqlite.org/index.html)
- [Uvicorn](https://www.uvicorn.org/)
- [Traefik](https://doc.traefik.io/traefik/)
- [Sqlite-Utils](https://pypi.org/project/sqlite-utils/)
- [MultipleDispatch](https://pypi.org/project/multipledispatch/)
- [Redis](https://redis.io/)
<!-- GETTING STARTED -->

## Getting Started

To get a local copy up and running follow these simple example steps.

---

### Dependency Installation

- Make sure to have python3 and pip installed on your computer.

  ```sh
    sudo apt update
    sudo apt install --yes python3-pip ruby-foreman sqlite3 httpie
  ```

- Clone the repo

  ```sh
  git clone <repo.git>
  ```

- Install FastAPI and other tools from requirements
  ```sh
    python3 -m pip install -r requirements.txt
  ```

---

## Project Setup

### Database Population

1. Seed the database! (you may need to change permissions on your local machine)
   ```sh
   ./bin/db_seed.sh
   ```

---

### Leaderboard Cronjob

1. make sure cron is running. if not use `sudo service cron start`

2. build leaderboard standalone app and load cronjob

   ```
   ./bin/init.sh
   ```

   _proceed to service start instructions_

---

### Service Start

1. In the root directory of the app folder, create a .env and set values for CHECKING_PORT and VALIDATION_PORT

   ```
   echo -e "CHECKING_PORT=5000\nTRACKING_PORT=5200\nVALIDATION_PORT=5500" > .env
   ```

2. Run the services
   ```sh
   foreman start
   ```

---

## Test Running Services

1. Travel to

   - `app` http://127.0.0.1:8080/docs

   _depends on the values inputted for which service you wish to test_

2. Once there you can test out the routes!
