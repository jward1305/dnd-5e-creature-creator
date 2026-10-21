--CTAS stands for CREATE TABLE AS SELECT, allowing you to create a table already populated from a source.
--Explain more;;;;;

CREATE OR REPLACE TABLE CreaturesRaw AS 
SELECT unnest(results, max_depth := 2) 
FROM read_json('{ROOT_DIR}/json_dump/creatures*.json');

CREATE OR REPLACE TABLE CreatureTypesRaw AS 
SELECT unnest(results, max_depth := 2) 
FROM read_json('{ROOT_DIR}/json_dump/creaturetypes.json');

CREATE OR REPLACE TABLE ConditionsRaw AS 
SELECT unnest(results, max_depth := 2) 
FROM read_json('{ROOT_DIR}/json_dump/conditions.json');

CREATE OR REPLACE TABLE DamageTypesRaw AS 
SELECT unnest(results, max_depth := 2) 
FROM read_json('{ROOT_DIR}/json_dump/damagetypes.json');

CREATE OR REPLACE TABLE EnvironmentsRaw AS 
SELECT unnest(results, max_depth := 2) 
FROM read_json('{ROOT_DIR}/json_dump/environments.json');

CREATE OR REPLACE TABLE LanguagesRaw AS 
SELECT unnest(results, max_depth := 2) 
FROM read_json('{ROOT_DIR}/json_dump/languages.json');

CREATE OR REPLACE TABLE SizesRaw AS 
SELECT unnest(results, max_depth := 2) 
FROM read_json('{ROOT_DIR}/json_dump/sizes.json');

CREATE OR REPLACE TABLE Traits AS 
SELECT
    row_number() OVER () As TraitID,
    *
    FROM(
        SELECT
            key AS CreatureKey, 
            unnest(traits, max_depth := 2) 
        FROM CreaturesRaw
    );

CREATE OR REPLACE TABLE Actions AS 
SELECT
    row_number() OVER () As ActionID,
    *
    FROM(
        SELECT
            key AS CreatureKey, 
            unnest(actions, max_depth := 2) 
        FROM CreaturesRaw
    );