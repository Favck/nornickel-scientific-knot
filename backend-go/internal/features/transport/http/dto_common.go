package transport_http

import "github.com/Favck/nornickel-scientific-knot/internal/core/domain"

type GraphPayloadDTO struct {
	OntologyName string                 `json:"ontology_name"`
	Version      string                 `json:"version"`
	Nodes        map[string][]EntityDTO `json:"nodes"`
	Edges        []RelationDTO          `json:"edges"`
}

type EntityDTO struct {
	ID             string    `json:"id"`
	Label          string    `json:"label,omitempty"`
	NameRu         string    `json:"name_ru,omitempty"`
	NameEn         string    `json:"name_en,omitempty"`
	Synonyms       []string  `json:"synonyms,omitempty"`
	Embedding      []float32 `json:"embedding,omitempty"`
	ParameterName  string    `json:"parameter_name,omitempty"`
	ValueRaw       string    `json:"value_raw,omitempty"`
	Operator       string    `json:"operator,omitempty"`
	ValueNumeric   *float64  `json:"value_numeric,omitempty"`
	ValueMin       *float64  `json:"value_min,omitempty"`
	ValueMax       *float64  `json:"value_max,omitempty"`
	Unit           string    `json:"unit,omitempty"`
	FullName       string    `json:"full_name,omitempty"`
	Organization   string    `json:"organization,omitempty"`
	Geography      string    `json:"geography,omitempty"`
	Title          string    `json:"title,omitempty"`
	Year           int       `json:"year,omitempty"`
	ProtocolNumber string    `json:"protocol_number,omitempty"`
	Date           string    `json:"date,omitempty"`
}

func (dto EntityDTO) ToDomain(label string) domain.Entity {
	return domain.Entity{
		ID:             dto.ID,
		Label:          label,
		NameRu:         dto.NameRu,
		NameEn:         dto.NameEn,
		Synonyms:       dto.Synonyms,
		Embedding:      dto.Embedding,
		ParameterName:  dto.ParameterName,
		ValueRaw:       dto.ValueRaw,
		Operator:       dto.Operator,
		ValueNumeric:   dto.ValueNumeric,
		ValueMin:       dto.ValueMin,
		ValueMax:       dto.ValueMax,
		Unit:           dto.Unit,
		FullName:       dto.FullName,
		Organization:   dto.Organization,
		Geography:      dto.Geography,
		Title:          dto.Title,
		Year:           dto.Year,
		ProtocolNumber: dto.ProtocolNumber,
		Date:           dto.Date,
	}
}

type RelationDTO struct {
	Type        string `json:"type"`
	Source      string `json:"source"`
	Target      string `json:"target"`
	Description string `json:"description,omitempty"`
}

func (dto RelationDTO) ToDomain() domain.Relation {
	return domain.Relation{
		From:        dto.Source,
		To:          dto.Target,
		Type:        dto.Type,
		Description: dto.Description,
	}
}

func PayloadToDomain(payload GraphPayloadDTO) domain.GraphPayload {
	var entities []domain.Entity
	for label, entitiesDTO := range payload.Nodes {
		for _, e := range entitiesDTO {
			entities = append(entities, e.ToDomain(label))
		}
	}

	relations := make([]domain.Relation, len(payload.Edges))
	for i, r := range payload.Edges {
		relations[i] = r.ToDomain()
	}

	return domain.NewGraphPayload(entities, relations)
}

type SearchRequestDTO struct {
	QueryVector []float32  `json:"query_vector"`
	Filters     FiltersDTO `json:"filters"`
}

type FiltersDTO struct {
	Geo     string       `json:"geo"`
	Numeric []NumericDTO `json:"numeric"`
}

type NumericDTO struct {
	RawEntity    string  `json:"raw_entity"`
	Operator     string  `json:"operator"`
	ValueNumeric float32 `json:"value_numeric"`
	Unit         string  `json:"unit"`
}

type PyvisGraphDTO struct {
	Nodes []PyvisNodeDTO `json:"nodes"`
	Edges []PyvisEdgeDTO `json:"edges"`
}

type PyvisNodeDTO struct {
	ID         string         `json:"id"`
	Label      string         `json:"label"`
	Group      string         `json:"group"`
	Properties map[string]any `json:"properties,omitempty"`
}

type PyvisEdgeDTO struct {
	From  string `json:"from"`
	To    string `json:"to"`
	Label string `json:"label"`
}

func DomainToPyvisNodeDTO(d domain.PyvisNode) PyvisNodeDTO {
	return PyvisNodeDTO{
		ID:         d.ID,
		Label:      d.Label,
		Group:      d.Group,
		Properties: d.Properties,
	}
}

func DomainToPyvisEdgeDTO(d domain.PyvisEdge) PyvisEdgeDTO {
	return PyvisEdgeDTO{
		From:  d.From,
		To:    d.To,
		Label: d.Label,
	}
}

func DomainToPyvisGraphDTO(d domain.PyvisGraph) PyvisGraphDTO {
	nodes := make([]PyvisNodeDTO, len(d.Nodes))
	for i, n := range d.Nodes {
		nodes[i] = DomainToPyvisNodeDTO(n)
	}

	edges := make([]PyvisEdgeDTO, len(d.Edges))
	for i, e := range d.Edges {
		edges[i] = DomainToPyvisEdgeDTO(e)
	}

	return PyvisGraphDTO{
		Nodes: nodes,
		Edges: edges,
	}
}

func (dto SearchRequestDTO) ToDomain() ([]float32, domain.SearchFilters) {
	numFilters := make([]domain.NumericFilter, len(dto.Filters.Numeric))
	for i, nf := range dto.Filters.Numeric {
		numFilters[i] = domain.NumericFilter{
			RawEntity:    nf.RawEntity,
			Operator:     nf.Operator,
			ValueNumeric: float64(nf.ValueNumeric),
			Unit:         nf.Unit,
		}
	}

	filters := domain.SearchFilters{
		Geo:     dto.Filters.Geo,
		Numeric: numFilters,
	}

	return dto.QueryVector, filters
}
