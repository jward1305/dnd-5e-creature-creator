-- sqlLinks.sql

CREATE OR REPLACE TABLE CreatureLanguages AS
SELECT DISTINCT
    c.key AS CreatureKey,
    l.key AS LKey
FROM CreaturesRaw AS c
CROSS JOIN UNNEST(c.languages.data) AS u(l);

CREATE OR REPLACE TABLE CreatureEnvironments AS
SELECT DISTINCT
    c.key AS CreatureKey,
    e.key AS EKey
FROM CreaturesRaw AS c
CROSS JOIN UNNEST(c.environments) AS u(e);

CREATE OR REPLACE TABLE CreatureConditionImmunities AS
SELECT DISTINCT
    c.key AS CreatureKey,
    ci.key AS CKey
FROM CreaturesRaw AS c
CROSS JOIN UNNEST(c.resistances_and_immunities.condition_immunities) AS u(ci);

CREATE OR REPLACE TABLE CreatureDamageRelationships AS
SELECT DISTINCT CreatureKey, DTKey, Relationship
FROM (
    SELECT c.key AS CreatureKey, d.key AS DTKey, 'immunity' AS Relationship
    FROM CreaturesRaw AS c
    CROSS JOIN UNNEST(c.resistances_and_immunities.damage_immunities) AS u(d)

    UNION ALL

    SELECT c.key, d.key, 'resistance'
    FROM CreaturesRaw AS c
    CROSS JOIN UNNEST(c.resistances_and_immunities.damage_resistances) AS u(d)

    UNION ALL

    SELECT c.key, d.key, 'vulnerability'
    FROM CreaturesRaw AS c
    CROSS JOIN UNNEST(c.resistances_and_immunities.damage_vulnerabilities) AS u(d)
);

-- sqlProficiencies.sql

-- 0 = none, 1 = proficient, 2 = expertise
-- Greatest function used for the few stat blocks that give no saving throw or skill bonuses.
CREATE OR REPLACE MACRO prof_level(bonus, score, prof) AS
    greatest(CAST(round((bonus - floor((score - 10) / 2.0)) / prof) AS INTEGER), 0);

CREATE OR REPLACE TABLE CreatureSaveProficiencies AS
SELECT
    s.CreatureKey,
    prof_level(r.saving_throws_all.strength,     s.Str, s.Proficiency_Bonus) AS Str_Prof,
    prof_level(r.saving_throws_all.dexterity,    s.Dex, s.Proficiency_Bonus) AS Dex_Prof,
    prof_level(r.saving_throws_all.constitution, s.Con, s.Proficiency_Bonus) AS Con_Prof,
    prof_level(r.saving_throws_all.intelligence, s.Int, s.Proficiency_Bonus) AS Int_Prof,
    prof_level(r.saving_throws_all.wisdom,       s.Wis, s.Proficiency_Bonus) AS Wis_Prof,
    prof_level(r.saving_throws_all.charisma,     s.Cha, s.Proficiency_Bonus) AS Cha_Prof
FROM CreaturesStructured AS s
JOIN CreaturesRaw AS r ON r.key = s.CreatureKey;

CREATE OR REPLACE TABLE CreatureSkillProficiencies AS
SELECT
    s.CreatureKey,
    -- STR
    prof_level(r.skill_bonuses_all.athletics,       s.Str, s.Proficiency_Bonus) AS Athletics_Prof,
    -- DEX
    prof_level(r.skill_bonuses_all.acrobatics,      s.Dex, s.Proficiency_Bonus) AS Acrobatics_Prof,
    prof_level(r.skill_bonuses_all.sleight_of_hand, s.Dex, s.Proficiency_Bonus) AS SleightOfHand_Prof,
    prof_level(r.skill_bonuses_all.stealth,         s.Dex, s.Proficiency_Bonus) AS Stealth_Prof,
    -- INT
    prof_level(r.skill_bonuses_all.arcana,          s.Int, s.Proficiency_Bonus) AS Arcana_Prof,
    prof_level(r.skill_bonuses_all.history,         s.Int, s.Proficiency_Bonus) AS History_Prof,
    prof_level(r.skill_bonuses_all.investigation,   s.Int, s.Proficiency_Bonus) AS Investigation_Prof,
    prof_level(r.skill_bonuses_all.nature,          s.Int, s.Proficiency_Bonus) AS Nature_Prof,
    prof_level(r.skill_bonuses_all.religion,        s.Int, s.Proficiency_Bonus) AS Religion_Prof,
    -- WIS
    prof_level(r.skill_bonuses_all.animal_handling, s.Wis, s.Proficiency_Bonus) AS AnimalHandling_Prof,
    prof_level(r.skill_bonuses_all.insight,         s.Wis, s.Proficiency_Bonus) AS Insight_Prof,
    prof_level(r.skill_bonuses_all.medicine,        s.Wis, s.Proficiency_Bonus) AS Medicine_Prof,
    prof_level(r.skill_bonuses_all.perception,      s.Wis, s.Proficiency_Bonus) AS Perception_Prof,
    prof_level(r.skill_bonuses_all.survival,        s.Wis, s.Proficiency_Bonus) AS Survival_Prof,
    -- CHA
    prof_level(r.skill_bonuses_all.deception,       s.Cha, s.Proficiency_Bonus) AS Deception_Prof,
    prof_level(r.skill_bonuses_all.intimidation,    s.Cha, s.Proficiency_Bonus) AS Intimidation_Prof,
    prof_level(r.skill_bonuses_all.performance,     s.Cha, s.Proficiency_Bonus) AS Performance_Prof,
    prof_level(r.skill_bonuses_all.persuasion,      s.Cha, s.Proficiency_Bonus) AS Persuasion_Prof
FROM CreaturesStructured AS s
JOIN CreaturesRaw AS r ON r.key = s.CreatureKey;

-- Rebuilds the statblock number from the stored level: mod + level * prof
CREATE OR REPLACE MACRO stat_bonus(score, level, prof) AS
    CAST(floor((score - 10) / 2.0) AS INTEGER) + level * prof;