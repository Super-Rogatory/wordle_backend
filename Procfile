# Define your services in a single Procfile and use foreman to start them both. Set the port for each service to use Foreman’s $PORT environment variable so that they will not conflict.
# foreman start checkings | foreman start validations | foreman start statistics

checkings: uvicorn --env-file ".env" --port $CHECKING_PORT --app-dir="./api" checking_service:app --reload
validations: uvicorn --env-file ".env" --port $VALIDATION_PORT --app-dir="./api" validation_service:app --reload
statistics: uvicorn --env-file ".env" --port $STATISTICS_PORT --app-dir="./api" statistics_service:app --reload
stats_1: NAME_OF_DB=stats_1 uvicorn --env-file ".env" --port $STATS1_PORT --app-dir="./api" statistics_service:app --reload
stats_2: NAME_OF_DB=stats_2 uvicorn --env-file ".env" --port $STATS2_PORT --app-dir="./api" statistics_service:app --reload
stats_3: NAME_OF_DB=stats_3 uvicorn --env-file ".env" --port $STATS3_PORT --app-dir="./api" statistics_service:app --reload