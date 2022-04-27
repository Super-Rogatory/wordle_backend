# Define your services in a single Procfile and use foreman to start them both. Set the port for each service to use Foreman’s $PORT environment variable so that they will not conflict.
# foreman start checkings | foreman start validations | foreman start statistics

<<<<<<< HEAD
checkings: uvicorn --port $PORT --app-dir="./api" checking_service:app --reload
validations: uvicorn --port $PORT --app-dir="./api" validation_service:app --reload
statistics: uvicorn--port $PORT --app-dir="./api" statistics_service:app --reload
stats: uvicorn --port $PORT --app-dir="./api" stats:app --reload
=======
checkings: uvicorn --env-file ".env" --port $CHECKING_PORT --app-dir="./api" checking_service:app --reload --root-path /api/checkings
validations: uvicorn --env-file ".env" --port $VALIDATION_PORT --app-dir="./api" validation_service:app --reload --root-path /api/validations
stats: uvicorn --env-file ".env" --port $STATS_PORT --app-dir="./api" statistics_service:app --reload --root-path /api/statistics
traefik: cd proxy && ./traefik 
>>>>>>> 593d45c946c9c169b5a5a95b7ed6449d33b0822d
