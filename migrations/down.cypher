MATCH (n) DETACH DELETE n;

DROP CONSTRAINT material_id_unique IF EXISTS;
DROP CONSTRAINT process_id_unique IF EXISTS;
DROP CONSTRAINT equipment_id_unique IF EXISTS;
DROP CONSTRAINT property_id_unique IF EXISTS;
DROP CONSTRAINT experiment_id_unique IF EXISTS;
DROP CONSTRAINT publication_id_unique IF EXISTS;
DROP CONSTRAINT expert_id_unique IF EXISTS;
DROP CONSTRAINT facility_id_unique IF EXISTS;

DROP INDEX property_value_num_index IF EXISTS;
DROP INDEX property_value_min_index IF EXISTS;
DROP INDEX property_value_max_index IF EXISTS;
DROP INDEX publication_year_index IF EXISTS;
DROP INDEX publication_geography_index IF EXISTS;
