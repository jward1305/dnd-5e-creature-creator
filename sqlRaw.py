import duckdb
from config import ROOT_DIR

DUCKDB_DIR = ROOT_DIR/"duckdb"/"CreatureCreator.duckdb"
DUCKDB_DIR.parent.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(str(DUCKDB_DIR))

file = ROOT_DIR/"sqlRaw.sql"
sql = file.read_text()
sql = sql.replace("{ROOT_DIR}", str(ROOT_DIR))
con.execute(sql)
con.table("CreaturesRaw").show()
con.table("CreatureTypesRaw").show()
con.table("ConditionsRaw").show()
con.table("DamageTypesRaw").show()
con.table("EnvironmentsRaw").show()
con.table("LanguagesRaw").show()
con.table("SizesRaw").show()
con.sql("SELECT descriptions FROM ConditionsRaw").show()
con.close()

'''


TABLE Creature:
{
    creatureid: SERIAL PRIMARY KEY,
    key: VARCHAR, 
    name: VARCHAR, 
    isCustom: BOOLEAN DEFAULT FALSE,
    type: INTEGER REFERENCES Creature_Types(typeid),
    size: INTEGER REFERENCES Sizes(sizeid),
    subcategory: VARCHAR,
    alignment: VARCHAR, 
    challenge_rating: DOUBLE, 
    experience_points: BIGINT, 
    armor_class: BIGINT, 
    armor_detail: VARCHAR, 
    hit_points: BIGINT, 
    hit_dice: VARCHAR, 
    str: INTEGER,
    dex: INTEGER,
    con: INTEGER,
    int: INTEGER,
    wis: INTEGER,
    cha: INTEGER,
    walk_speed: INTEGER,
    fly_speed: INTEGER,
    swim_speed: INTEGER,
    climb_speed: INTEGER,
    burrow_speed: INTEGER,
    crawl_speed: INTEGER,
    canHover: BOOLEAN,
    passive_perception: INTEGER, 
    normal_sight_range: INTEGER,
    darkvision_range: INTEGER, 
    blindsight_range: INTEGER, 
    tremorsense_range: INTEGER, 
    true_sight_range: INTEGER, 
    languages_display: VARCHAR, 
    damage_immunities_display: VARCHAR, 
    damage_resistances_display: VARCHAR,
    damage_vulnerabilities_display:VARCHAR,
}

TABLE Creature_Types: #https://api.open5e.com/v2/creaturetypes/ where results/descriptions/gamesystem == 5e-2014
{
    typeid: SERIAL PRIMARY KEY,
    key: VARCHAR,
    name: VARCHAR,
    desc: VARCHAR
}

TABLE Sizes: #https://api.open5e.com/v2/sizes/?document__gamesystem__key__iexact=5e-2014
{
    sizeid: SERIAL PRIMARY KEY,
    key: VARCHAR,
    name: VARCHAR,
    rank: INTEGER,
    space_diameter: INTEGER,
    suggested_hit_dice: VARCHAR
}

TABLE Damage_Types: #https://api.open5e.com/v2/damagetypes/ where results/descriptions/gamesystem == 5e-2014
{
    damageid: SERIAL PRIMARY KEY,
    key: VARCHAR,
    name: VARCHAR,
    desc: VARCHAR
}

TABLE Conditions: #https://api.open5e.com/v2/conditions/?document__gamesystem__key__iexact=5e-2014
{
    conditionid: SERIAL PRIMARY KEY,
    key: VARCHAR,
    name: VARCHAR,
    desc: VARCHAR,      #where results/descriptions/gamesystem == 5e-2014
}

TABLE Environments: #https://api.open5e.com/v2/environments/?document__key__in=core%2C+srd-2014
{
    environmentid: SERIAL PRIMARY KEY,
    key: VARCHAR,
    name: VARCHAR,
    desc: VARCHAR
}

TABLE Languages: #https://api.open5e.com/v2/languages/?document__gamesystem__key__iexact=5e-2014
{
    languageid: SERIAL PRIMARY KEY,
    key: VARCHAR,
    name: VARCHAR,
    desc: VARCHAR,
    script: VARCHAR,
    isExotic: BOOLEAN,
    isSecret: BOOLEAN
}

TABLE Creature_Save_Proficiencies:   #derive proficiencies from saving_throws
{
    creatureid INTEGER REFERENCES Creature(creatureid) ON DELETE CASCADE,
    str_prof: BOOLEAN,
    dex_prof: BOOLEAN,
    con_prof: BOOLEAN,
    int_prof: BOOLEAN,
    wis_prof: BOOLEAN,
    cha_prof: BOOLEAN,
}

TABLE Creature_Skill_Proficiencies: #derive proficienciesfrom skill_bonus
{
    creatureid INTEGER REFERENCES Creature(creatureid) ON DELETE CASCADE,
    acrobatics_prof: BOOLEAN, 
    animal_handling_prof: BOOLEAN, 
    arcana_prof: BOOLEAN, 
    athletics_prof: BOOLEAN,
    deception_prof: BOOLEAN, 
    history_prof: BOOLEAN, 
    insight_prof: BOOLEAN, 
    intimidation_prof: BOOLEAN, 
    investigation_prof: BOOLEAN, 
    medicine_prof: BOOLEAN, 
    nature_prof: BOOLEAN, 
    perception_prof: BOOLEAN, 
    performance_prof: BOOLEAN, 
    persuasion_prof: BOOLEAN, 
    religion_prof: BOOLEAN, 
    sleight_of_hand_prof: BOOLEAN, 
    stealth_prof: BOOLEAN, 
    survival: BOOLEAN,
}

CREATE TYPE damagerelationship AS ENUM ('resistance', 'immunity', 'vulnerability')
TABLE Creature_Damage_Relationships:
{
   creatureid: INTEGER REFERENCES Creature(creatureid) ON DELETE CASCADE,
   damageid: INTEGER REFERENCES Damage_Types(damageid),
   relationship: damagerelationship
   PRIMARY KEY (creatureid, damageid)

}

TABLE Creature_Environment:
{
   creatureid: INTEGER REFERENCES Creature(creatureid) ON DELETE CASCADE,
   environmentid: INTEGER REFERENCES Environments(environmentid),
   PRIMARY KEY (creatureid, environmentid)
}

TABLE Creature_Condition_Immunities:
{
   creatureid: INTEGER REFERENCES Creature(creatureid) ON DELETE CASCADE,
   conditionid: INTEGER REFERENCES Conditions(conditionid),
   PRIMARY KEY (creatureid, conditionid)
}

TABLE Creature_Languages:
{
   creatureid: INTEGER REFERENCES Creature(creatureid) ON DELETE CASCADE,
   languageid: INTEGER REFERENCES Languages(languageid),
   PRIMARY KEY (creatureid, languageid)
}

'''
