traefik: ./proxy/traefik --configFile=./proxy/traefik.toml
checkings: uvicorn --port $CHECKING_PORT --app-dir="./api" checking_service:app --reload --root-path /api/checkings
validations: uvicorn --port $VALIDATION_PORT --app-dir="./api" validation_service:app --reload --root-path /api/validations
stats: uvicorn --port $PORT --app-dir="./api" statistics_service:app --reload --root-path /api/statistics
redis: redis-server
