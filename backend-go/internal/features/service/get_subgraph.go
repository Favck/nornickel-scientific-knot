package service

import (
	"context"

	"github.com/Favck/nornickel-scientific-knot/internal/core/domain"
)

func (s *Service) GetSubgraph(
	ctx context.Context,
	queryVector []float32,
	filters domain.SearchFilters,
) (domain.PyvisGraph, error) {
	pyvisGraph, err := s.repository.GetSubgraph(ctx, queryVector, filters)
	if err != nil {
		return domain.PyvisGraph{}, err
	}

	validNodes := make(map[string]domain.PyvisNode)
	for _, node := range pyvisGraph.Nodes {
		if !passesFilters(node, filters) {
			continue
		}
		validNodes[node.ID] = node
	}

	var validEdges []domain.PyvisEdge
	edgeDegrees := make(map[string]int)

	for _, edge := range pyvisGraph.Edges {
		if _, okFrom := validNodes[edge.From]; okFrom {
			if _, okTo := validNodes[edge.To]; okTo {
				validEdges = append(validEdges, edge)
				edgeDegrees[edge.From]++
				edgeDegrees[edge.To]++
			}
		}
	}

	var finalNodes []domain.PyvisNode
	for _, node := range validNodes {
		if edgeDegrees[node.ID] > 0 || len(validEdges) == 0 {
			finalNodes = append(finalNodes, node)
		}
	}

	pyvisGraph.Nodes = finalNodes
	pyvisGraph.Edges = validEdges

	return pyvisGraph, nil
}

func passesFilters(node domain.PyvisNode, filters domain.SearchFilters) bool {
	if filters.Geo != "" {
		if geo, ok := node.Properties["geography"].(string); ok && geo != "" {
			if geo != filters.Geo {
				return false
			}
		}
	}

	if len(filters.Numeric) > 0 {
		for _, nf := range filters.Numeric {
			var val float64
			var hasVal bool
			if v, ok := node.Properties["value_numeric"].(float64); ok {
				val = v
				hasVal = true
			} else if v, ok := node.Properties["value_numeric"].(int64); ok {
				val = float64(v)
				hasVal = true
			}

			if hasVal {
				if unit, ok := node.Properties["unit"].(string); ok && unit != "" && unit != nf.Unit {
					continue
				}

				switch nf.Operator {
				case "<":
					if !(val < nf.ValueNumeric) {
						return false
					}
				case "<=":
					if !(val <= nf.ValueNumeric) {
						return false
					}
				case ">":
					if !(val > nf.ValueNumeric) {
						return false
					}
				case ">=":
					if !(val >= nf.ValueNumeric) {
						return false
					}
				case "=":
					if val != nf.ValueNumeric {
						return false
					}
				}
			}
		}
	}

	return true
}
