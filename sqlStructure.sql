CREATE OR REPLACE TABLE CreaturesStructured AS
SELECT
	key AS CreatureKey,
	name AS CreatureName,
	FALSE AS isCustom,
	type.key AS CreatureType,
	size.key AS CreatureSize,
	challenge_rating AS Challenge_Rating,
	CAST(
		CASE
			WHEN challenge_rating < 1 THEN 2
			ELSE 2 + floor((challenge_rating - 1) / 4)
		END
		AS INTEGER
	) AS Proficiency_Bonus,
	experience_points AS Experience_Points,
	armor_class AS Armour_Class,
	armor_detail AS Armour_Details,
	hit_points AS Hit_Points,
	hit_dice AS Hit_Dice,
	ability_scores.strength AS Str,
	ability_scores.dexterity AS Dex,
	ability_scores.constitution AS Con,
	ability_scores.intelligence AS Int,
	ability_scores.wisdom AS Wis,
	ability_scores.charisma AS Cha,
	speed_all.walk AS Walk_Speed,
	speed_all.fly AS Fly_Speed,
	speed_all.swim AS Swim_Speed,
	speed_all.climb AS Climb_Speed,
	speed_all.burrow AS Burrow_Speed,
	speed_all.crawl AS Crawl_Speed,
	speed_all.hover AS canHover,
	passive_perception AS Passive_Perception,
	normal_sight_range AS Normal_Sight_Range,
	darkvision_range AS Darkvision_Range,
	blindsight_range AS Blindsight_Range,
	tremorsense_range AS Tremorsense_Range,
	truesight_range AS True_Sight_Range,
	languages.as_string AS Languages_Display,
	resistances_and_immunities.damage_immunities_display AS Damage_Immunities_Display,
	resistances_and_immunities.damage_resistances_display AS Damage_Resistances_Display,
	resistances_and_immunities.damage_vulnerabilities_display AS Damage_Vulnerabilities_Display 
FROM CreaturesRaw;

CREATE OR REPLACE TABLE CreatureTypesStructured AS
SELECT
    ct.key AS CTKey,
    ct.name AS CTName,
    d.desc AS CTDescription
FROM CreatureTypesRaw AS ct
CROSS JOIN UNNEST(ct.descriptions) AS u(d)
WHERE d.gamesystem = '5e-2014';

CREATE OR REPLACE TABLE ConditionsStructured AS
SELECT
	c.key AS CKey,
	c.name AS CName,
	d.desc AS CDescription
FROM ConditionsRaw AS c
CROSS JOIN UNNEST(c.descriptions) AS u(d)
WHERE d.gamesystem = '5e-2014';

CREATE OR REPLACE TABLE DamageTypesStructured AS
SELECT
	dt.key AS DTKey,
	dt.name AS DTName,
	d.desc AS DTDescription
FROM  DamageTypesRaw AS dt
CROSS JOIN UNNEST(dt.descriptions) AS u(d)
WHERE d.gamesystem = '5e-2014';

CREATE OR REPLACE TABLE EnvironmentsStructured AS
SELECT
	e.key AS EKey,
	e.name AS EName,
	e.desc AS EDescription,
	e.aquatic AS isAquatic,
	e.planar AS isPlanar,
	e.interior AS isInterior
FROM EnvironmentsRaw AS e;

CREATE OR REPLACE TABLE LanguagesStructured AS
SELECT
	l.key AS LKey,
	l.name AS LName,
	l.desc AS LDescription,
	l.script_language AS LScript,
	l.is_exotic AS isExotic,
	l.is_Secret AS isSecret
FROM LanguagesRaw AS l;

CREATE OR REPLACE TABLE SizesStructured AS
SELECT
	s.key AS SKey,
	s.name AS SName,
	s.rank as SRank,
	s.space_diameter AS Diameter,
	s.suggested_hit_dice AS SuggestedHitDice
FROM SizesRaw AS s;