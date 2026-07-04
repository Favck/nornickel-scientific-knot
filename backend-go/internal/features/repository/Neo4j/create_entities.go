package neo4j_repository

import (
	"context"
	"fmt"

	"github.com/Favck/nornickel-scientific-knot/internal/core/domain"
	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

func (r *Repository) CreateEntities(
	ctx context.Context,
	payload domain.GraphPayload,
) error {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer session.Close(ctx)

	_, err := session.ExecuteWrite(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		var entitiesParams []map[string]any
		for _, e := range payload.Entities {
			entitiesParams = append(entitiesParams, map[string]any{
				"id":              e.ID,
				"label":           e.Label,
				"name_ru":         e.NameRu,
				"name_en":         e.NameEn,
				"synonyms":        e.Synonyms,
				"parameter_name":  e.ParameterName,
				"value_raw":       e.ValueRaw,
				"operator":        e.Operator,
				"value_numeric":   e.ValueNumeric,
				"value_min":       e.ValueMin,
				"value_max":       e.ValueMax,
				"unit":            e.Unit,
				"full_name":       e.FullName,
				"organization":    e.Organization,
				"geography":       e.Geography,
				"title":           e.Title,
				"year":            e.Year,
				"protocol_number": e.ProtocolNumber,
				"date":            e.Date,
			})
		}

		var relationsParams []map[string]any
		for _, rel := range payload.Relations {
			relationsParams = append(relationsParams, map[string]any{
				"from":        rel.From,
				"to":          rel.To,
				"type":        rel.Type,
				"description": rel.Description,
			})
		}

		query := `
			UNWIND $entities AS e
			CALL apoc.merge.node([e.label], {id: e.id}, {
				name_ru: e.name_ru,
				name_en: e.name_en,
				synonyms: e.synonyms,
				parameter_name: e.parameter_name,
				value_raw: e.value_raw,
				operator: e.operator,
				value_numeric: e.value_numeric,
				value_min: e.value_min,
				value_max: e.value_max,
				unit: e.unit,
				full_name: e.full_name,
				organization: e.organization,
				geography: e.geography,
				title: e.title,
				year: e.year,
				protocol_number: e.protocol_number,
				date: e.date
			}, {}) YIELD node AS entity
			
			WITH count(entity) as c
			
			UNWIND $relations AS r
			MATCH (from {id: r.from}), (to {id: r.to})
			CALL apoc.create.relationship(from, r.type, {description: r.description}, to) YIELD rel
			
			RETURN count(rel)
		`

		params := map[string]any{
			"entities":  entitiesParams,
			"relations": relationsParams,
		}

		result, err := tx.Run(ctx, query, params)
		if err != nil {
			return nil, err
		}

		return result.Consume(ctx)
	})

	if err != nil {
		return fmt.Errorf("neo4j transaction failed: %w", err)
	}

	return nil
}
