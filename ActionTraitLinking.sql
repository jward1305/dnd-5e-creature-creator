CREATE OR REPLACE SEQUENCE seq_traitid START 1;

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

CREATE OR REPLACE TABLE TraitsFiltered(
    TraitID INTEGER PRIMARY KEY DEFAULT NEXTVAL('seq_traitid'),
    TName VARCHAR,
    TDescription VARCHAR
);

INSERT INTO TraitsFiltered (TName, TDescription)
SELECT DISTINCT 
    name, 
    "desc"
FROM Traits;

CREATE OR REPLACE TABLE CreatureTraits(
    TraitID INTEGER REFERENCES TraitsFiltered(TraitID),
    CreatureKey VARCHAR REFERENCES CreaturesStructured(CreatureKey),
    PRIMARY KEY(TraitID, CreatureKey)
);

INSERT INTO CreatureTraits
SELECT DISTINCT
    tf.TraitID,
    t.CreatureKey
FROM Traits AS t
INNER JOIN TraitsFiltered as tf
ON tf.TName = t.name AND tf.TDescription = t."desc";

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

CREATE OR REPLACE TABLE CreatureActions(
    CreatureActionID INTEGER PRIMARY KEY,
    CreatureKey VARCHAR REFERENCES CreaturesStructured(CreatureKey),
    CAName VARCHAR,
    CADescription VARCHAR,
);

CREATE OR REPLACE SEQUENCE seq_attackid START 1;

CREATE OR REPLACE TABLE Attacks (
    AttackID INTEGER PRIMARY KEY DEFAULT NEXTVAL('seq_attackid'),
    CreatureActionID INTEGER REFERENCES CreatureActions(CreatureActionID),
    AName VARCHAR,
    ToHit INTEGER,
    Reach INTEGER,
    ARange INTEGER,
    ALongRange INTEGER,
    TargetCreatureOnly BOOLEAN,
    DamageDieCount INTEGER,
    DamageDieType VARCHAR,
    DamageBonus INTEGER,
    DamageType VARCHAR,
    ExtraDamageDieCount INTEGER,
    ExtraDamageDieType VARCHAR,
    ExtraDamageBonus INTEGER,
    ExtraDamageType VARCHAR,
);