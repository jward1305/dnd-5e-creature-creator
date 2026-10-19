CREATE OR REPLACE TABLE Actions AS 
SELECT 
    key AS CreatureKey, 
    unnest(actions, max_depth := 2) 
FROM CreaturesRaw;

CREATE OR REPLACE TABLE Traits AS 
SELECT 
    key AS CreatureKey, 
    unnest(traits, max_depth := 2) 
FROM CreaturesRaw;