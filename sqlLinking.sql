

CREATE OR REPLACE TABLE CreatureLanguages(
    CreatureKey VARCHAR REFERENCES CreaturesStructured(CreatureKey),
    LKey VARCHAR REFERENCES LanguagesStructured(LKey),
    PRIMARY KEY(CreatureKey, LKey)
);

INSERT INTO CreatureLanguages
SELECT DISTINCT
    c.key,
    l.key
FROM CreaturesRaw AS c
CROSS JOIN unnest(c.languages.data) AS u(l);

CREATE OR REPLACE TABLE CreatureEnvironments(
    CreatureKey VARCHAR REFERENCES CreaturesStructured(CreatureKey),
    EKey VARCHAR REFERENCES EnvironmentsStructured(EKey),
    PRIMARY KEY(CreatureKey, EKey)
);

INSERT INTO CreatureEnvironments
SELECT DISTINCT
    c.key,
    e.key
FROM CreaturesRaw AS c
CROSS JOIN unnest(c.environments) AS u(e);

CREATE OR REPLACE TABLE CreatureConditionImmunities(
    CreatureKey VARCHAR REFERENCES CreaturesStructured(CreatureKey),
    CKey VARCHAR REFERENCES ConditionsStructured(CKey),
    PRIMARY KEY(CreatureKey, CKey)
);

INSERT INTO CreatureConditionImmunities
SELECT DISTINCT
    c.key,
    ci.key
FROM CreaturesRaw AS c
CROSS JOIN unnest(c.resistances_and_immunities.condition_immunities) AS u(ci);

CREATE TYPE IF NOT EXISTS damage_relationship AS ENUM(
    'immunity',
    'resistance',
    'vulnerability'
);

CREATE OR REPLACE TABLE CreatureDamageRelationships(
    CreatureKey VARCHAR REFERENCES CreaturesStructured(CreatureKey),
    DTKey VARCHAR REFERENCES DamageTypesStructured(DTKey),
    Relationship damage_relationship,
    PRIMARY KEY(CreatureKey, DTKey, Relationship)  --Relationship in PK as creatures cannot have mutliple relationships with a single 
);                                                 --damage type

INSERT INTO CreatureDamageRelationships
SELECT DISTINCT CreatureKey, DTKey, Relationship
FROM (
    SELECT 
    c.key AS CreatureKey, 
    d.key AS DTKey, 
    'immunity' AS Relationship
    FROM CreaturesRaw AS c
    CROSS JOIN unnest(c.resistances_and_immunities.damage_immunities) AS u(d)

    UNION ALL

    SELECT 
    c.key, 
    d.key, 
    'resistance'
    FROM CreaturesRaw AS c
    CROSS JOIN unnest(c.resistances_and_immunities.damage_resistances) AS u(d)

    UNION ALL

    SELECT 
    c.key, 
    d.key, 
    'vulnerability'
    FROM CreaturesRaw AS c
    CROSS JOIN unnest(c.resistances_and_immunities.damage_vulnerabilities) AS u(d)
);

-- 0 = none, 1 = proficient, 2 = expertise
-- Works out if the proficiency bonus of a stat is affected by proficiency or expertise.
-- Also used to identify saving throw proficiencies.
-- Use the greatest function for the few stat blocks that give no saving throw or skill bonuses.
CREATE OR REPLACE MACRO prof_level(bonus, score, prof) AS
    greatest(CAST(round((bonus - floor((score - 10) / 2.0)) / prof) AS INTEGER), 0);

CREATE OR REPLACE TABLE CreatureSkillProficiencies(
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

INSERT INTO CreatureSkillProficiencies
SELECT
    s.CreatureKey,
    -- Str
    prof_level(r.skill_bonuses_all.athletics,       s.Str, s.Proficiency_Bonus),
    -- Dex
    prof_level(r.skill_bonuses_all.acrobatics,      s.Dex, s.Proficiency_Bonus),
    prof_level(r.skill_bonuses_all.sleight_of_hand, s.Dex, s.Proficiency_Bonus),
    prof_level(r.skill_bonuses_all.stealth,         s.Dex, s.Proficiency_Bonus),
    -- Int
    prof_level(r.skill_bonuses_all.arcana,          s.Int, s.Proficiency_Bonus),
    prof_level(r.skill_bonuses_all.history,         s.Int, s.Proficiency_Bonus),
    prof_level(r.skill_bonuses_all.investigation,   s.Int, s.Proficiency_Bonus),
    prof_level(r.skill_bonuses_all.nature,          s.Int, s.Proficiency_Bonus),
    prof_level(r.skill_bonuses_all.religion,        s.Int, s.Proficiency_Bonus),
    -- Wis
    prof_level(r.skill_bonuses_all.animal_handling, s.Wis, s.Proficiency_Bonus),
    prof_level(r.skill_bonuses_all.insight,         s.Wis, s.Proficiency_Bonus),
    prof_level(r.skill_bonuses_all.medicine,        s.Wis, s.Proficiency_Bonus),
    prof_level(r.skill_bonuses_all.perception,      s.Wis, s.Proficiency_Bonus),
    prof_level(r.skill_bonuses_all.survival,        s.Wis, s.Proficiency_Bonus),
    -- Cha
    prof_level(r.skill_bonuses_all.deception,       s.Cha, s.Proficiency_Bonus),
    prof_level(r.skill_bonuses_all.intimidation,    s.Cha, s.Proficiency_Bonus),
    prof_level(r.skill_bonuses_all.performance,     s.Cha, s.Proficiency_Bonus),
    prof_level(r.skill_bonuses_all.persuasion,      s.Cha, s.Proficiency_Bonus)
FROM CreaturesStructured AS s
INNER JOIN CreaturesRaw AS r ON r.key = s.CreatureKey;

CREATE OR REPLACE TABLE CreatureSaveProficiencies (
    CreatureKey VARCHAR PRIMARY KEY REFERENCES CreaturesStructured(CreatureKey),
    Str_Prof TINYINT,
    Dex_Prof TINYINT,
    Con_Prof TINYINT,
    Int_Prof TINYINT,
    Wis_Prof TINYINT,
    Cha_Prof TINYINT,
);

INSERT INTO CreatureSaveProficiencies --Works out prof level using macro
SELECT
    s.CreatureKey,
    prof_level(r.saving_throws_all.strength,     s.Str, s.Proficiency_Bonus),
    prof_level(r.saving_throws_all.dexterity,    s.Dex, s.Proficiency_Bonus),
    prof_level(r.saving_throws_all.constitution, s.Con, s.Proficiency_Bonus),
    prof_level(r.saving_throws_all.intelligence, s.Int, s.Proficiency_Bonus),
    prof_level(r.saving_throws_all.wisdom,       s.Wis, s.Proficiency_Bonus),
    prof_level(r.saving_throws_all.charisma,     s.Cha, s.Proficiency_Bonus)
FROM CreaturesStructured AS s
INNER JOIN CreaturesRaw AS r ON r.key = s.CreatureKey;