package domain

type GraphPayload struct {
	Entities  []Entity
	Relations []Relation
}

type Relation struct {
	From        string
	To          string
	Type        string
	Description string
}

type Entity struct {
	ID             string
	Label          string
	NameRu         string
	NameEn         string
	Synonyms       []string
	ParameterName  string
	ValueRaw       string
	Operator       string
	ValueNumeric   *float64
	ValueMin       *float64
	ValueMax       *float64
	Unit           string
	FullName       string
	Organization   string
	Geography      string
	Title          string
	Year           int
	ProtocolNumber string
	Date           string
}

func NewGraphPayload(
	entities []Entity,
	relations []Relation,
) GraphPayload {
	return GraphPayload{
		Entities:  entities,
		Relations: relations,
	}
}
