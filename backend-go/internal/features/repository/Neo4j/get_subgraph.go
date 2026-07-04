package neo4j_repository

import (
	"context"
	"fmt"

	"github.com/Favck/nornickel-scientific-knot/internal/core/domain"
	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
)

func (r *Repository) GetSubgraph(
	ctx context.Context,
	queryVector []float32,
	filters domain.SearchFilters,
) (domain.PyvisGraph, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	result, err := session.ExecuteRead(ctx, func(tx neo4j.ManagedTransaction) (any, error) {
		query := `
			MATCH (n)
			WHERE n.embedding IS NOT NULL
			WITH n,
				 REDUCE(s = 0.0, i IN range(0, size(n.embedding)-1) | s + n.embedding[i] * $query_vector[i]) AS dot,
				 REDUCE(s = 0.0, i IN range(0, size(n.embedding)-1) | s + n.embedding[i] * n.embedding[i]) AS norm_n,
				 REDUCE(s = 0.0, i IN range(0, size($query_vector)-1) | s + $query_vector[i] * $query_vector[i]) AS norm_q
			WITH n, CASE WHEN norm_n > 0 AND norm_q > 0 THEN dot / (sqrt(norm_n) * sqrt(norm_q)) ELSE 0 END AS score
			ORDER BY score DESC
			LIMIT 1

			MATCH path = (n)-[*1..2]-(m)

			UNWIND nodes(path) AS node
			UNWIND relationships(path) AS rel
			
			RETURN collect(DISTINCT node) AS nodes, 
			       collect(DISTINCT {
			           from: startNode(rel).id, 
			           to: endNode(rel).id, 
			           label: type(rel)
			       }) AS edges
		`

		params := map[string]any{
			"query_vector": queryVector,
		}

		res, err := tx.Run(ctx, query, params)
		if err != nil {
			return nil, err
		}

		var record *neo4j.Record
		if res.Next(ctx) {
			record = res.Record()
		} else {
			return domain.PyvisGraph{}, nil
		}
		if err := res.Err(); err != nil {
			return nil, err
		}

		var pyvisGraph domain.PyvisGraph

		rawNodes, _ := record.Get("nodes")
		if rawNodes != nil {
			for _, rawNode := range rawNodes.([]any) {
				dbNode := rawNode.(neo4j.Node)
				
				labels := dbNode.Labels
				var group string
				if len(labels) > 0 {
					group = labels[0]
				}

				props := dbNode.Props
				id, _ := props["id"].(string)
				
				label := id
				if nameRu, ok := props["name_ru"].(string); ok && nameRu != "" {
					label = nameRu
				} else if title, ok := props["title"].(string); ok && title != "" {
					label = title
				} else if param, ok := props["parameter_name"].(string); ok && param != "" {
					label = param
				} else if fullName, ok := props["full_name"].(string); ok && fullName != "" {
					label = fullName
				}

				pyvisGraph.Nodes = append(pyvisGraph.Nodes, domain.PyvisNode{
					ID:         id,
					Label:      label,
					Group:      group,
					Properties: props,
				})
			}
		}

		rawEdges, _ := record.Get("edges")
		if rawEdges != nil {
			for _, rawEdge := range rawEdges.([]any) {
				edgeMap := rawEdge.(map[string]any)
				
				from, _ := edgeMap["from"].(string)
				to, _ := edgeMap["to"].(string)
				label, _ := edgeMap["label"].(string)

				pyvisGraph.Edges = append(pyvisGraph.Edges, domain.PyvisEdge{
					From:  from,
					To:    to,
					Label: label,
				})
			}
		}

		return pyvisGraph, nil
	})

	if err != nil {
		return domain.PyvisGraph{}, fmt.Errorf("neo4j search failed: %w", err)
	}

	return result.(domain.PyvisGraph), nil
}
