# Define your services in a single Procfile and use foreman to start them both. Set the port for each service to use Foreman’s $PORT environment variable so that they will not conflict.
# foreman start checkings | foreman start validations | foreman start statistics

checkings: uvicorn --env-file ".env" --port $CHECKING_PORT --app-dir="./api" checking_service:app --reload
validations: uvicorn --env-file ".env" --port $VALIDATION_PORT --app-dir="./api" validation_service:app --reload
statistics: uvicorn --env-file ".env" --port $STATISTICS_PORT --app-dir="./api" statistics_service:app --reload
