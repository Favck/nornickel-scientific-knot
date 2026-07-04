include ../.env
export

export PROJECT_ROOT=${shell pwd}

app-run:
	@export LOGGER_FOLDER="./out/logs" && \
	go mod tidy && \
	go run ./cmd/main.go