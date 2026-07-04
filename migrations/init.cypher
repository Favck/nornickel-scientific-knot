CREATE CONSTRAINT material_id_unique IF NOT EXISTS FOR (n:Material) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT process_id_unique IF NOT EXISTS FOR (n:Process) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT equipment_id_unique IF NOT EXISTS FOR (n:Equipment) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT property_id_unique IF NOT EXISTS FOR (n:Property) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT experiment_id_unique IF NOT EXISTS FOR (n:Experiment) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT publication_id_unique IF NOT EXISTS FOR (n:Publication) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT expert_id_unique IF NOT EXISTS FOR (n:Expert) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT facility_id_unique IF NOT EXISTS FOR (n:Facility) REQUIRE n.id IS UNIQUE;

CREATE INDEX property_value_num_index IF NOT EXISTS FOR (n:Property) ON (n.value_numeric);
CREATE INDEX property_value_min_index IF NOT EXISTS FOR (n:Property) ON (n.value_min);
CREATE INDEX property_value_max_index IF NOT EXISTS FOR (n:Property) ON (n.value_max);

CREATE INDEX publication_year_index IF NOT EXISTS FOR (n:Publication) ON (n.year);
CREATE INDEX publication_geography_index IF NOT EXISTS FOR (n:Publication) ON (n.geography);
