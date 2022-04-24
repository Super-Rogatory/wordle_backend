# Define your services in a single Procfile and use foreman to start them both. Set the port for each service to use Foreman’s $PORT environment variable so that they will not conflict.
# foreman start checkings | foreman start validations | foreman start statistics

traefik: ./traefik --configFile=./etc/traefik.toml
checkings: uvicorn --env-file ".env" --port $PORT --app-dir="./api" checking_service:app --reload
validations: uvicorn --env-file ".env" --port $PORT --app-dir="./api" validation_service:app --reload
stats: uvicorn --port $PORT stats:app --reload
