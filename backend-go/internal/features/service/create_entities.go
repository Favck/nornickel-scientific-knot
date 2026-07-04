package service

import (
	"context"
	"fmt"

	"github.com/Favck/nornickel-scientific-knot/internal/core/domain"
)

func (s *Service) CreateEntities(
	ctx context.Context,
	payload domain.GraphPayload,
) error {
	if len(payload.Entities) == 0 {
		return fmt.Errorf("no entities to process")
	}

	if err := s.repository.CreateEntities(ctx, payload); err != nil {
		return fmt.Errorf("create entities: %w", err)
	}

	return nil
}
