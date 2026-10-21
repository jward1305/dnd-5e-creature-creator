CREATE TABLE IF NOT EXISTS CreatureLanguages(
    CreatureKey VARCHAR REFERENCES CreaturesStructured(CreatureKey),
    LKey VARCHAR REFERENCES LanguagesStructured(LKey),
    PRIMARY KEY(CreatureKey, LKey)
);

CREATE TABLE IF NOT EXISTS CreatureEnvironments(
    CreatureKey VARCHAR REFERENCES CreaturesStructured(CreatureKey),
    EKey VARCHAR REFERENCES EnvironmentsStructured(EKey),
    PRIMARY KEY(CreatureKey, EKey)
);

CREATE TABLE IF NOT EXISTS CreatureConditionImmunities(
    CreatureKey VARCHAR REFERENCES CreaturesStructured(CreatureKey),
    CKey VARCHAR REFERENCES ConditionsStructured(CKey),
    PRIMARY KEY(CreatureKey, CKey)
);

CREATE TYPE IF NOT EXISTS damage_relationship AS ENUM(
    'immunity',
    'resistance',
    'vulnerability'
);

CREATE TABLE IF NOT EXISTS CreatureDamageRelationships(
    CreatureKey VARCHAR REFERENCES CreaturesStructured(CreatureKey),
    DTKey VARCHAR REFERENCES DamageTypesStructured(DTKey),
    Relationship damage_relationship,
    PRIMARY KEY(CreatureKey, DTKey, Relationship)  --Relationship in PK as creatures cannot have mutliple relationships with a single 
);                                                 --damage type

CREATE OR REPLACE MACRO prof_level(bonus, score, prof) AS
    greatest(CAST(round((bonus - floor((score - 10) / 2.0)) / prof) AS INTEGER), 0);

CREATE TABLE IF NOT EXISTS CreatureSkillProficiencies(
    CreatureKey VARCHAR PRIMARY KEY REFERENCES CreaturesStructured(CreatureKey),
    Athletics_Prof TINYINT,
    Acrobatics_Prof TINYINT,
    SleightOfHand_Prof TINYINT,
    Stealth_Prof TINYINT,
    Arcana_Prof TINYINT,
    History_Prof TINYINT,
    Investigation_Prof TINYINT,
    Nature_Prof TINYINT,
    Religion_Prof TINYINT,
    AnimalHandling_Prof TINYINT,
    Insight_Prof TINYINT,
    Medicine_Prof TINYINT,
    Perception_Prof TINYINT,
    Survival_Prof TINYINT,
    Deception_Prof TINYINT,
    Intimidation_Prof TINYINT,
    Performance_Prof TINYINT,
    Persuasion_Prof TINYINT
);

CREATE TABLE IF NOT EXISTS CreatureSaveProficiencies (
    CreatureKey VARCHAR PRIMARY KEY REFERENCES CreaturesStructured(CreatureKey),
    Str_Prof TINYINT,
    Dex_Prof TINYINT,
    Con_Prof TINYINT,
    Int_Prof TINYINT,
    Wis_Prof TINYINT,
    Cha_Prof TINYINT,
);

--Can't drop sequences due to dependencies and no built in function to restart them
--so on a data refresh, sequence based ids will simply continue on from the last value
CREATE SEQUENCE IF NOT EXISTS seq_traitid START 1; 

CREATE TABLE IF NOT EXISTS TraitsFiltered(
    TraitID INTEGER PRIMARY KEY DEFAULT NEXTVAL('seq_traitid'),
    TName VARCHAR,
    TDescription VARCHAR
);

CREATE TABLE IF NOT EXISTS CreatureTraits(
    TraitID INTEGER REFERENCES TraitsFiltered(TraitID),
    CreatureKey VARCHAR REFERENCES CreaturesStructured(CreatureKey),
    PRIMARY KEY(TraitID, CreatureKey)
);

CREATE TABLE IF NOT EXISTS CreatureActions(
    CreatureActionID INTEGER PRIMARY KEY,
    CreatureKey VARCHAR REFERENCES CreaturesStructured(CreatureKey),
    CAName VARCHAR,
    CADescription VARCHAR,
);

CREATE SEQUENCE IF NOT EXISTS seq_attackid START 1;

CREATE TABLE IF NOT EXISTS Attacks (
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