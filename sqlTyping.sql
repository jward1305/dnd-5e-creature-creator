CREATE OR REPLACE TABLE CreaturesTyped AS
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
FROM CreaturesRaw