traefik: ./proxy/traefik --configFile=./proxy/traefik.toml
checkings: uvicorn --port $CHECKING_PORT --app-dir="./api" checking_service:app --reload --root-path /api/checkings
validations: uvicorn --port $VALIDATION_PORT --app-dir="./api" validation_service:app --reload --root-path /api/validations
<<<<<<< HEAD
=======
trackings: uvicorn --port $TRACKING_PORT --app-dir="./api" tracking_service:app --reload --reload --root-path /api/trackings
>>>>>>> 04d8b201e1c2b69665bf3fa3fbba5ab19d49615a
stats: uvicorn --port $PORT --app-dir="./api" statistics_service:app --reload --root-path /api/statistics
redis: redis-server
