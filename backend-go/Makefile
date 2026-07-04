include ../.env
export

export PROJECT_ROOT=${shell pwd}

app-run:
	@export LOGGER_FOLDER=${PROJECT_ROOT}/out/logs && \
	go mod tidy && \
	go run ${PROJECT_ROOT}/cmd/main.go