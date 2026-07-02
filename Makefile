include .env
export

export PROJECT_ROOT=${shell pwd}

up:
	@mkdir -p migrations
	touch migrations/init.cypher
	docker-compose up -d

migrate:
	@docker-compose run --rm neo4j-init

down:
	@docker-compose down
