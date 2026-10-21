CREATE OR REPLACE TABLE CreaturesStructured (
	CreatureKey VARCHAR PRIMARY KEY,
	CreatureName VARCHAR,
	isCustom BOOLEAN,
	CreatureType VARCHAR,
	CreatureSize VARCHAR,
	Challenge_Rating DOUBLE,
	Proficiency_Bonus INTEGER,
	Experience_Points INTEGER,
	Armour_Class TINYINT,
	Armour_Details VARCHAR,
	Hit_Points SMALLINT,
	Hit_Dice VARCHAR,
	Str TINYINT,
	Dex TINYINT,
	Con TINYINT,
	Int TINYINT,
	Wis TINYINT,
	Cha TINYINT,
	Walk_Speed SMALLINT,
	Fly_Speed SMALLINT,
	Swim_Speed SMALLINT,
	Climb_Speed SMALLINT,
	Burrow_Speed SMALLINT,
	Crawl_Speed SMALLINT,
	canHover BOOLEAN,
	Passive_Perception SMALLINT,
	Normal_Sight_Range SMALLINT,
	Darkvision_Range SMALLINT,
	Blindsight_Range SMALLINT,
	Tremorsense_Range SMALLINT,
	True_Sight_Range SMALLINT,
	Languages_Display VARCHAR,
	Damage_Immunities_Display VARCHAR,
	Damage_Resistances_Display VARCHAR,
	Damage_Vulnerabilities_Display VARCHAR 
);


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

CREATE OR REPLACE TABLE CreatureTypesStructured(
	CTKey VARCHAR PRIMARY KEY,
	CTName VARCHAR,
	CTDescription VARCHAR
);

INSERT INTO CreatureTypesStructured
SELECT
    ct.key,
    ct.name,
    d.desc
FROM CreatureTypesRaw AS ct
CROSS JOIN UNNEST(ct.descriptions) AS u(d)
WHERE d.gamesystem = '5e-2014';

CREATE OR REPLACE TABLE ConditionsStructured(
	CKey VARCHAR PRIMARY KEY,
	CName VARCHAR,
	CDescription VARCHAR
);

INSERT INTO ConditionsStructured
SELECT
	c.key,
	c.name,
	d.desc
FROM ConditionsRaw AS c
CROSS JOIN UNNEST(c.descriptions) AS u(d)
WHERE d.gamesystem = '5e-2014';

CREATE OR REPLACE TABLE DamageTypesStructured(
	DTKey VARCHAR PRIMARY KEY,
	DTName VARCHAR,
	DTDescription VARCHAR
);
INSERT INTO DamageTypesStructured
SELECT
	dt.key,
	dt.name,
	d.desc
FROM  DamageTypesRaw AS dt
CROSS JOIN UNNEST(dt.descriptions) AS u(d)
WHERE d.gamesystem = '5e-2014';

CREATE OR REPLACE TABLE EnvironmentsStructured(
	EKey VARCHAR PRIMARY KEY,
	EName VARCHAR,
	EDescription VARCHAR,
	isAquatic BOOLEAN,
	isPlanar BOOLEAN,
	isInterior BOOLEAN
);

INSERT INTO EnvironmentsStructured
SELECT
	e.key,
	e.name,
	e.desc,
	e.aquatic,
	e.planar,
	e.interior
FROM EnvironmentsRaw AS e;

CREATE OR REPLACE TABLE LanguagesStructured(
	LKey VARCHAR PRIMARY KEY,
	LName VARCHAR,
	LDescription VARCHAR,
	LScript VARCHAR,
	isExotic BOOLEAN,
	isSecret BOOLEAN
);

INSERT INTO LanguagesStructured
SELECT
	l.key,
	l.name,
	l.desc,
	l.script_language,
	l.is_exotic,
	l.is_Secret
FROM LanguagesRaw AS l;

CREATE OR REPLACE TABLE SizesStructured(
	SKey VARCHAR PRIMARY KEY,
	SName VARCHAR,
	SRank INTEGER,
	Diamter VARCHAR,
	SuggestedHitDice VARCHAR
);

INSERT INTO SizesStructured
SELECT
	s.key,
	s.name,
	s.rank,
	s.space_diameter,
	s.suggested_hit_dice
FROM SizesRaw AS s;