--Delete and insert data from table. Performed atomically to ensure no conflicts or failures.
--Done seperately due to issues with CREATE OR REPLACE when foreign keys and dependencies are involved.

----------------------------------------------------Structured Tables
------------------CreaturesStructured
BEGIN TRANSACTION;

DELETE FROM CreaturesStructured;

INSERT INTO CreaturesStructured
SELECT
	key,
	name,
	FALSE,
	type.key,
	size.key,
	challenge_rating,
	CAST(
		CASE
			WHEN challenge_rating < 1 THEN 2
			ELSE 2 + floor((challenge_rating - 1) / 4)
		END
		AS INTEGER
	),
	experience_points,
	armor_class,
	armor_detail,
	hit_points,
	hit_dice,
	ability_scores.strength,
	ability_scores.dexterity,
	ability_scores.constitution,
	ability_scores.intelligence,
	ability_scores.wisdom,
	ability_scores.charisma,
	speed_all.walk,
	speed_all.fly,
	speed_all.swim,
	speed_all.climb,
	speed_all.burrow,
	speed_all.crawl,
	speed_all.hover,
	passive_perception,
	normal_sight_range,
	darkvision_range,
	blindsight_range,
	tremorsense_range,
	truesight_range,
	languages.as_string,
	resistances_and_immunities.damage_immunities_display,
	resistances_and_immunities.damage_resistances_display,
	resistances_and_immunities.damage_vulnerabilities_display 
FROM CreaturesRaw;

COMMIT;
------------------CreatureTypesStructured
BEGIN TRANSACTION;

DELETE FROM CreatureTypesStructured;

INSERT INTO CreatureTypesStructured
SELECT
    ct.key,
    ct.name,
    d.desc
FROM CreatureTypesRaw AS ct
CROSS JOIN UNNEST(ct.descriptions) AS u(d)
WHERE d.gamesystem = '5e-2014';

COMMIT;
------------------ConditionsStructured
BEGIN TRANSACTION;

DELETE FROM ConditionsStructured;

INSERT INTO ConditionsStructured
SELECT
	c.key,
	c.name,
	d.desc
FROM ConditionsRaw AS c
CROSS JOIN UNNEST(c.descriptions) AS u(d)
WHERE d.gamesystem = '5e-2014';

COMMIT;
------------------DamageTypesStructured
BEGIN TRANSACTION;

DELETE FROM DamageTypesStructured;

INSERT INTO DamageTypesStructured
SELECT
	dt.key,
	dt.name,
	d.desc
FROM  DamageTypesRaw AS dt
CROSS JOIN UNNEST(dt.descriptions) AS u(d)
WHERE d.gamesystem = '5e-2014';

COMMIT;
------------------EnvironmentsStructured
BEGIN TRANSACTION;

DELETE FROM EnvironmentsStructured;

INSERT INTO EnvironmentsStructured
SELECT
	e.key,
	e.name,
	e.desc,
	e.aquatic,
	e.planar,
	e.interior
FROM EnvironmentsRaw AS e;

COMMIT;
------------------LanguagesStructured
BEGIN TRANSACTION;

DELETE FROM LanguagesStructured;

INSERT INTO LanguagesStructured
SELECT
	l.key,
	l.name,
	l.desc,
	l.script_language,
	l.is_exotic,
	l.is_Secret
FROM LanguagesRaw AS l;

COMMIT;
------------------SizesStructured
BEGIN TRANSACTION;

DELETE FROM SizesStructured;

INSERT INTO SizesStructured
SELECT
	s.key,
	s.name,
	s.rank,
	s.space_diameter,
	s.suggested_hit_dice
FROM SizesRaw AS s;

COMMIT;
----------------------------------------------------Linking Tables
------------------CreatureLanguages
BEGIN TRANSACTION;

DELETE FROM CreatureLanguages;

INSERT INTO CreatureLanguages
SELECT DISTINCT
    c.key,
    l.key
FROM CreaturesRaw AS c
CROSS JOIN unnest(c.languages.data) AS u(l);

COMMIT;
------------------CreatureEnvironments
BEGIN TRANSACTION;

DELETE FROM CreatureEnvironments;

INSERT INTO CreatureEnvironments
SELECT DISTINCT
    c.key,
    e.key
FROM CreaturesRaw AS c
CROSS JOIN unnest(c.environments) AS u(e);

COMMIT;
------------------CreatureConditionImmunities
BEGIN TRANSACTION;

DELETE FROM CreatureConditionImmunities;

INSERT INTO CreatureConditionImmunities
SELECT DISTINCT
    c.key,
    ci.key
FROM CreaturesRaw AS c
CROSS JOIN unnest(c.resistances_and_immunities.condition_immunities) AS u(ci);

COMMIT;
------------------CreatureDamageRelationships
BEGIN TRANSACTION;

DELETE FROM CreatureDamageRelationships;

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

COMMIT;
------------------CreatureSkillProficiencies
BEGIN TRANSACTION;

DELETE FROM CreatureSkillProficiencies;

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

COMMIT;
------------------CreatureSaveProficiencies
BEGIN TRANSACTION;

DELETE FROM CreatureSaveProficiencies;

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

COMMIT;
----------------------------------------------------Trait & Action Tables
--The Action and Attack tables are populated by attackparsing.py
------------------TraitsFiltered
BEGIN TRANSACTION;

DELETE FROM TraitsFiltered;

INSERT INTO TraitsFiltered (TName, TDescription)
SELECT DISTINCT 
    name, 
    "desc"
FROM Traits;

COMMIT;
------------------CreatureTraits
BEGIN TRANSACTION;

DELETE FROM CreatureTraits;

INSERT INTO CreatureTraits
SELECT DISTINCT
    tf.TraitID,
    t.CreatureKey
FROM Traits AS t
INNER JOIN TraitsFiltered as tf
ON tf.TName = t.name AND tf.TDescription = t."desc";

COMMIT;