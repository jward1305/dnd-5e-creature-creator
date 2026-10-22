BEGIN TRANSACTION;

INSERT OR REPLACE INTO CreaturesStructured
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

INSERT OR REPLACE INTO CreatureTypesStructured
SELECT
    ct.key,
    ct.name,
    d.desc
FROM CreatureTypesRaw AS ct
CROSS JOIN UNNEST(ct.descriptions) AS u(d)
WHERE d.gamesystem = '5e-2014';

INSERT OR REPLACE INTO ConditionsStructured
SELECT
	c.key,
	c.name,
	d.desc
FROM ConditionsRaw AS c
CROSS JOIN UNNEST(c.descriptions) AS u(d)
WHERE d.gamesystem = '5e-2014';

INSERT OR REPLACE INTO DamageTypesStructured
SELECT
	dt.key,
	dt.name,
	d.desc
FROM  DamageTypesRaw AS dt
CROSS JOIN UNNEST(dt.descriptions) AS u(d)
WHERE d.gamesystem = '5e-2014';

INSERT OR REPLACE INTO EnvironmentsStructured
SELECT
	e.key,
	e.name,
	e.desc,
	e.aquatic,
	e.planar,
	e.interior
FROM EnvironmentsRaw AS e;

INSERT OR REPLACE INTO LanguagesStructured
SELECT
	l.key,
	l.name,
	l.desc,
	l.script_language,
	l.is_exotic,
	l.is_Secret
FROM LanguagesRaw AS l;

INSERT OR REPLACE INTO SizesStructured
SELECT
	s.key,
	s.name,
	s.rank,
	s.space_diameter,
	s.suggested_hit_dice
FROM SizesRaw AS s;

--Uses INSERT INTO and ON CONFLICT due to having both a primary key and a unique constraint
INSERT INTO TraitsFiltered (TName, TDescription)
SELECT DISTINCT 
    name, 
    "desc"
FROM Traits
ON CONFLICT (TName, TDescription) DO NOTHING;

COMMIT;