INSERT OR REPLACE INTO CreatureLanguages
SELECT DISTINCT
    c.key,
    l.key
FROM CreaturesRaw AS c
CROSS JOIN unnest(c.languages.data) AS u(l);

INSERT OR REPLACE INTO CreatureEnvironments
SELECT DISTINCT
    c.key,
    e.key
FROM CreaturesRaw AS c
CROSS JOIN unnest(c.environments) AS u(e);

INSERT OR REPLACE INTO CreatureConditionImmunities
SELECT DISTINCT
    c.key,
    ci.key
FROM CreaturesRaw AS c
CROSS JOIN unnest(c.resistances_and_immunities.condition_immunities) AS u(ci);

INSERT OR REPLACE INTO CreatureDamageRelationships
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

INSERT OR REPLACE INTO CreatureSkillProficiencies
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

INSERT OR REPLACE INTO CreatureSaveProficiencies --Works out prof level using macro
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

INSERT OR REPLACE INTO CreatureTraits
SELECT DISTINCT
    tf.TraitID,
    t.CreatureKey
FROM Traits AS t
INNER JOIN TraitsFiltered as tf
ON tf.TName = t.name AND tf.TDescription = t."desc";