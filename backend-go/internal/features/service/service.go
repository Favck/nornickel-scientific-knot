package service

import (
	"context"

	"github.com/Favck/nornickel-scientific-knot/internal/core/domain"
)

type Service struct {
	repository Repository
}

type Repository interface {
	CreateEntities(
		ctx context.Context,
		payload domain.GraphPayload,
	) error
	GetSubgraph(
		ctx context.Context,
		queryVector []float32,
		filters domain.SearchFilters,
	) (domain.PyvisGraph, error)
}

func NewService(
	repository Repository,
) *Service {
	return &Service{
		repository: repository,
	}
}
