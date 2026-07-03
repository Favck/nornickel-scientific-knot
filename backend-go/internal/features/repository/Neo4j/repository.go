package neo4j_repository

import "github.com/neo4j/neo4j-go-driver/v5/neo4j"

type Repository struct {
	driver neo4j.DriverWithContext
}

func NewRepository(
	driver neo4j.DriverWithContext,
) *Repository {
	return &Repository{
		driver: driver,
	}
}
