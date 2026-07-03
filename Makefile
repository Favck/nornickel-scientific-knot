include .env
export

export PROJECT_ROOT=${shell pwd}

up:
	@mkdir -p migrations
	touch migrations/init.cypher
	touch migrations/down.cypher
	docker-compose up -d

migrate:
	@docker-compose run --rm neo4j-init

down:
	@docker-compose down

env-cleanup:
	@read -p "Очистить все volume файлы окружения? Опасность утери данных. [y/N]: " ans; \
	if [ "$$ans" = "y" ]; then \
		docker compose down neo4j && \
		rm -rf backend-go/out/neo4j_data && \
		echo "Файлы окружения очищены"; \
	else \
		echo "Очистка окружения отменена"; \
	fi

logs_cleanup:
	@read -p "Очистить все log файлы? Опасность утери логов. [y/N]: " ans; \
	if [ "$$ans" = "y" ]; then \
		rm -rf backend-go/out/logs && \
		echo "Файлы логов очищены"; \
	else \
		echo "Очистка логов отменена"; \
	fi

migrate-down:
	@docker-compose run --rm neo4j-init bash -c "cypher-shell -a neo4j://neo4j:7687 -u ${NEO4J_USER} -p ${NEO4J_PASSWORD} -f /migrations/down.cypher"
