package transport_http

import "github.com/Favck/nornickel-scientific-knot/internal/core/domain"

type GraphPayloadDTO struct {
	OntologyName string                 `json:"ontology_name"`
	Version      string                 `json:"version"`
	Nodes        map[string][]EntityDTO `json:"nodes"`
	Edges        []RelationDTO          `json:"edges"`
}

type EntityDTO struct {
	ID             string   `json:"id"`
	Label          string   `json:"label,omitempty"`
	NameRu         string   `json:"name_ru,omitempty"`
	NameEn         string   `json:"name_en,omitempty"`
	Synonyms       []string `json:"synonyms,omitempty"`
	ParameterName  string   `json:"parameter_name,omitempty"`
	ValueRaw       string   `json:"value_raw,omitempty"`
	Operator       string   `json:"operator,omitempty"`
	ValueNumeric   *float64 `json:"value_numeric,omitempty"`
	ValueMin       *float64 `json:"value_min,omitempty"`
	ValueMax       *float64 `json:"value_max,omitempty"`
	Unit           string   `json:"unit,omitempty"`
	FullName       string   `json:"full_name,omitempty"`
	Organization   string   `json:"organization,omitempty"`
	Geography      string   `json:"geography,omitempty"`
	Title          string   `json:"title,omitempty"`
	Year           int      `json:"year,omitempty"`
	ProtocolNumber string   `json:"protocol_number,omitempty"`
	Date           string   `json:"date,omitempty"`
}

func (dto EntityDTO) ToDomain(label string) domain.Entity {
	return domain.Entity{
		ID:             dto.ID,
		Label:          label,
		NameRu:         dto.NameRu,
		NameEn:         dto.NameEn,
		Synonyms:       dto.Synonyms,
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
