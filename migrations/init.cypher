CREATE CONSTRAINT article_name_unique IF NOT EXISTS FOR (a:Article) REQUIRE a.name IS UNIQUE;

CREATE CONSTRAINT entity_name_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE;
