# Define your services in a single Procfile and use foreman to start them both. Set the port for each service to use Foreman’s $PORT environment variable so that they will not conflict.
# foreman start checkings | foreman start validations

checkings: uvicorn --env-file ".env" --port $CHECKING_PORT checking_service:app --reload
validations: uvicorn --env-file ".env" --port $VALIDATION_PORT validation_service:app --reload
test: uvicorn --env-file ".env" --port $VALIDATION_PORT validation_service:app --reload