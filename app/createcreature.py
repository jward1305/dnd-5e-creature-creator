from __future__ import annotations

import math
import sys
import uuid
from pathlib import Path
from typing import Any

import duckdb
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import query_database
from config import DUCKDB_DIR


CR_VALUES = [0, 0.125, 0.25, 0.5, 
             1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 
             11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30]

SKILL_PROFICIENCIES = (
    ("Athletics", "Athletics_Prof"),
    ("Acrobatics", "Acrobatics_Prof"),
    ("Sleight of Hand", "SleightOfHand_Prof"),
    ("Stealth", "Stealth_Prof"),
    ("Arcana", "Arcana_Prof"),
    ("History", "History_Prof"),
    ("Investigation", "Investigation_Prof"),
    ("Nature", "Nature_Prof"),
    ("Religion", "Religion_Prof"),
    ("Animal Handling", "AnimalHandling_Prof"),
    ("Insight", "Insight_Prof"),
    ("Medicine", "Medicine_Prof"),
    ("Perception", "Perception_Prof"),
    ("Survival", "Survival_Prof"),
    ("Deception", "Deception_Prof"),
    ("Intimidation", "Intimidation_Prof"),
    ("Performance", "Performance_Prof"),
    ("Persuasion", "Persuasion_Prof"),
)
SAVE_PROFICIENCIES = (
    ("Strength", "Str_Prof"),
    ("Dexterity", "Dex_Prof"),
    ("Constitution", "Con_Prof"),
    ("Intelligence", "Int_Prof"),
    ("Wisdom", "Wis_Prof"),
    ("Charisma", "Cha_Prof"),
)

con = duckdb.connect(str(DUCKDB_DIR))
cColumns = con.sql("DESCRIBE CreaturesStructured").fetchall()
CREATURE_COLUMNS = tuple([row[0] for row in cColumns])
aColumns = con.sql("DESCRIBE Attacks").fetchall()
ATTACK_COLUMNS = tuple(
    row[0] for row in aColumns
    if row[0] not in ("AttackID", "CreatureActionID")
)
con.close()

def fetch_rows(
    connection: duckdb.DuckDBPyConnection,
    query: str,
    parameters: tuple[Any, ...] = (),
) -> list[tuple[Any, ...]]:
    return connection.execute(query, list(parameters)).fetchall()


def save_creature(
    name: str,
    creature_type: str,
    size: str,
    challenge_rating: float,
    experience_points: int,
    armour_class: int,
    armour_details: str,
    hit_points: int,
    hit_dice: str,
    ability_scores: tuple[int, int, int, int, int, int],
    speeds: tuple[int, int, int, int, int, int],
    can_hover: bool,
    senses: tuple[int, int, int, int, int, int],
    language_keys: list[str],
    environments: list[tuple[str, str]],
    condition_keys: list[str],
    damage_relationships: list[tuple[str, str]],
    skill_proficiencies: list[str],
    save_proficiencies: list[str],
    trait_ids: list[int],
    action_ids: list[int],
) -> str:
    kName = name.replace(" ", "-")
    creature_key = f"custom_{kName}"
    proficiency_bonus = (
        2 if challenge_rating < 1
        else 2 + math.floor((challenge_rating - 1) / 4)
    )
    language_rows: list[tuple[str, str]] = []
    damage_names: dict[str, list[str]] = {
        "immunity": [],
        "resistance": [],
        "vulnerability": []
    }

    connection = duckdb.connect(str(DUCKDB_DIR))
    try:
        connection.execute("BEGIN TRANSACTION")
        if language_keys:
            language_rows = fetch_rows(
                connection,
                "SELECT LKey, LName FROM LanguagesStructured WHERE LKey IN ("
                + ", ".join("?" for _ in language_keys)
                + ") ORDER BY LName",
                tuple(language_keys)
            )
        damage_name_by_key = dict(fetch_rows(
            connection,
            "SELECT DTKey, DTName FROM DamageTypesStructured"
        ))
        damage_names = {key: [] for key in damage_names}
        for damage_key, relationship in damage_relationships:
            if damage_key in damage_name_by_key:
                damage_names[relationship].append(damage_name_by_key[damage_key])

        creature_values: tuple[Any, ...] = (
            creature_key,
            name.strip(),
            True,
            creature_type,
            size,
            challenge_rating,
            proficiency_bonus,
            experience_points,
            armour_class,
            armour_details.strip() or None,
            hit_points,
            hit_dice.strip() or None,
            *ability_scores,
            *speeds,
            can_hover,
            *senses,
            ", ".join(language_name for _, language_name in language_rows) or None,
            ", ".join(damage_names["immunity"]) or None,
            ", ".join(damage_names["resistance"]) or None,
            ", ".join(damage_names["vulnerability"]) or None,
        )
        placeholders = ", ".join("?" for _ in CREATURE_COLUMNS)
        connection.execute(
            f"INSERT INTO CreaturesStructured ({', '.join(CREATURE_COLUMNS)}) "
            f"VALUES ({placeholders})",
            list(creature_values),
        )

        if language_rows:
            connection.executemany(
                "INSERT INTO CreatureLanguages (CreatureKey, LKey) VALUES (?, ?)",
                [(creature_key, language_key) for language_key, _ in language_rows]
            )
        if environments:
            connection.executemany(
                "INSERT INTO CreatureEnvironments (CreatureKey, EKey) VALUES (?, ?)",
                [(creature_key, environment_key) for environment_key, _ in environments]
            )
        if condition_keys:
            connection.executemany(
                "INSERT INTO CreatureConditionImmunities (CreatureKey, CKey) VALUES (?, ?)",
                [(creature_key, condition_key) for condition_key in condition_keys]
            )
        if damage_relationships:
            connection.executemany(
                """
                INSERT INTO CreatureDamageRelationships (CreatureKey, DTKey, Relationship)
                VALUES (?, ?, ?)
                """,
                [
                    (creature_key, damage_key, relationship)
                    for damage_key, relationship in damage_relationships
                ],
            )
        skill_columns = [column for _, column in SKILL_PROFICIENCIES]
        connection.execute(
            f"""
            INSERT INTO CreatureSkillProficiencies
                (CreatureKey, {', '.join(skill_columns)})
            VALUES ({', '.join('?' for _ in range(len(skill_columns) + 1))})
            """,
            [creature_key]
            + [int(column in skill_proficiencies) for column in skill_columns],
        )
        save_columns = [column for _, column in SAVE_PROFICIENCIES]
        connection.execute(
            f"""
            INSERT INTO CreatureSaveProficiencies
                (CreatureKey, {', '.join(save_columns)})
            VALUES ({', '.join('?' for _ in range(len(save_columns) + 1))})
            """,
            [creature_key]
            + [int(column in save_proficiencies) for column in save_columns],
        )
        if trait_ids:
            connection.executemany(
                "INSERT INTO CreatureTraits (TraitID, CreatureKey) VALUES (?, ?)",
                [(trait_id, creature_key) for trait_id in trait_ids]
            )

        if action_ids:
            next_action_id = fetch_rows(
                connection,
                "SELECT coalesce(max(CreatureActionID), 0) + 1 FROM CreatureActions",
            )[0][0]
            action_query = """
                SELECT CAName, CADescription
                FROM CreatureActions
                WHERE CreatureActionID = ?
            """
            attack_query = (
                f"SELECT {', '.join(ATTACK_COLUMNS)} FROM Attacks "
                "WHERE CreatureActionID = ? ORDER BY AttackID"
            )
            insert_action = """
                INSERT INTO CreatureActions
                    (CreatureActionID, CreatureKey, CAName, CADescription)
                VALUES (?, ?, ?, ?)
            """
            insert_attack = f"""
                INSERT INTO Attacks (CreatureActionID, {', '.join(ATTACK_COLUMNS)})
                VALUES ({', '.join('?' for _ in range(len(ATTACK_COLUMNS) + 1))})
            """
            for source_action_id in action_ids:
                source_action = fetch_rows(
                    connection, action_query, (source_action_id,)
                )
                if not source_action:
                    continue
                action_name, action_description = source_action[0]
                connection.execute(
                    insert_action,
                    [next_action_id, creature_key, action_name, action_description]
                )
                source_attacks = fetch_rows(
                    connection, attack_query, (source_action_id,)
                )
                if source_attacks:
                    connection.executemany(
                        insert_attack,
                        [
                            (next_action_id, *attack_values)
                            for attack_values in source_attacks
                        ]
                    )
                next_action_id += 1

        connection.execute("COMMIT")
    except Exception:
        connection.execute("ROLLBACK")
        raise
    finally:
        connection.close()
    return creature_key

st.title("Create Custom Creature")
st.caption(
    "Choose an existing creature to prefill editable stats and defenses, then "
    "optionally copy traits and actions from the library."
)

if not DUCKDB_DIR.is_file():
    st.error(f"Database not found at `{DUCKDB_DIR}`. Build the database before creating a creature.")
    st.stop()

try:
    connection = duckdb.connect(str(DUCKDB_DIR), read_only=True)
    creature_types = fetch_rows(
        connection, "SELECT CTKey, CTName FROM CreatureTypesStructured ORDER BY CTName"
    )
    sizes = fetch_rows(
        connection, "SELECT SKey, SName, SuggestedHitDice FROM SizesStructured ORDER BY SRank"
    )
    languages = fetch_rows(
        connection, "SELECT LKey, LName FROM LanguagesStructured ORDER BY LName"
    )
    environments = fetch_rows(
        connection, "SELECT EKey, EName FROM EnvironmentsStructured ORDER BY EName"
    )
    conditions = fetch_rows(
        connection, "SELECT CKey, CName FROM ConditionsStructured ORDER BY CName"
    )
    damage_types = fetch_rows(
        connection, "SELECT DTKey, DTName FROM DamageTypesStructured ORDER BY DTName"
    )
    copy_creatures = fetch_rows(
        connection,
        "SELECT CreatureKey, CreatureName FROM CreaturesStructured ORDER BY CreatureName"
    )
    connection.close()
except duckdb.Error as error:
    st.error(f"Could not load options for creature creation: {error}")
    st.stop()

if not creature_types or not sizes:
    st.error("Creature types and sizes must be populated before creating a custom creature.")
    st.stop()

copy_source = st.selectbox(
    "Copy stats from an existing creature (optional)",
    options=[(None, "Select a creature"), *copy_creatures],
    format_func=lambda creature: creature[1],
    key="custom_copy_source"
)
copy_source_key = copy_source[0]

if "custom_previous_copy_source" not in st.session_state:
    st.session_state["custom_previous_copy_source"] = copy_source_key
elif st.session_state["custom_previous_copy_source"] != copy_source_key:
    st.session_state["custom_form_version"] = (
        st.session_state.get("custom_form_version", 0) + 1
    )
    st.session_state["custom_previous_copy_source"] = copy_source_key

copy_stats: dict[str, Any] = {}
copy_languages: list[str] = []
copy_environments: list[str] = []
copy_conditions: list[str] = []
copy_damage_relationships: list[str] = []
copy_skill_proficiencies: list[str] = []
copy_save_proficiencies: list[str] = []
copy_traits: list[int] = []
copy_actions: list[int] = []
if copy_source_key is not None:
    try:
        copy_stats_row = query_database(
            """
            SELECT
                CreatureType, CreatureSize, Challenge_Rating, Experience_Points,
                Armour_Class, Armour_Details, Hit_Points, Hit_Dice,
                Str, Dex, Con, Int, Wis, Cha,
                Walk_Speed, Fly_Speed, Swim_Speed, Climb_Speed, Burrow_Speed,
                Crawl_Speed, canHover, Passive_Perception, Normal_Sight_Range,
                Darkvision_Range, Blindsight_Range, Tremorsense_Range,
                True_Sight_Range
            FROM CreaturesStructured
            WHERE CreatureKey = ?
            """,
            (copy_source_key,)
        )
        if not copy_stats_row:
            st.error("Could not find the selected creature to copy.")
            st.stop()
        copy_stats = dict(zip(
            (
                "creature_type", "size", "challenge_rating", "experience_points",
                "armour_class", "armour_details", "hit_points", "hit_dice",
                "str", "dex", "con", "int", "wis", "cha",
                "walk", "fly", "swim", "climb", "burrow", "crawl", "hover",
                "perception", "normal_sight", "darkvision", "blindsight",
                "tremorsense", "truesight"
            ),
            copy_stats_row[0]
        ))
        copy_languages = [
            row[0] for row in query_database(
                """
                SELECT l.LName
                FROM CreatureLanguages AS cl
                JOIN LanguagesStructured AS l ON l.LKey = cl.LKey
                WHERE cl.CreatureKey = ?
                """,
                (copy_source_key,)
            )
        ]
        copy_environments = [
            row[0] for row in query_database(
                """
                SELECT e.EName
                FROM CreatureEnvironments AS ce
                JOIN EnvironmentsStructured AS e ON e.EKey = ce.EKey
                WHERE ce.CreatureKey = ?
                """,
                (copy_source_key,)
            )
        ]
        copy_conditions = [
            row[0] for row in query_database(
                """
                SELECT c.CName
                FROM CreatureConditionImmunities AS ci
                JOIN ConditionsStructured AS c ON c.CKey = ci.CKey
                WHERE ci.CreatureKey = ?
                """,
                (copy_source_key,)
            )
        ]
        copy_damage_relationships = [
            f"{damage_name} - {relationship.title()}"
            for damage_name, relationship in query_database(
                """
                SELECT d.DTName, cdr.Relationship
                FROM CreatureDamageRelationships AS cdr
                JOIN DamageTypesStructured AS d ON d.DTKey = cdr.DTKey
                WHERE cdr.CreatureKey = ?
                """,
                (copy_source_key,)
            )
        ]
        skill_rows = query_database(
            f"""
            SELECT {', '.join(column for _, column in SKILL_PROFICIENCIES)}
            FROM CreatureSkillProficiencies
            WHERE CreatureKey = ?
            """,
            (copy_source_key,),
        )
        if skill_rows:
            copy_skill_proficiencies = [
                column
                for (_, column), value in zip(SKILL_PROFICIENCIES, skill_rows[0])
                if value is not None and value > 0
            ]
        save_rows = query_database(
            f"""
            SELECT {', '.join(column for _, column in SAVE_PROFICIENCIES)}
            FROM CreatureSaveProficiencies
            WHERE CreatureKey = ?
            """,
            (copy_source_key,),
        )
        if save_rows:
            copy_save_proficiencies = [
                column
                for (_, column), value in zip(SAVE_PROFICIENCIES, save_rows[0])
                if value is not None and value > 0
            ]
        trait_options = query_database(
                """
                SELECT
                    t.TraitID,
                    t.TName,
                    t.TDescription,
                    min(c.CreatureName) AS SourceCreature
                FROM TraitsFiltered AS t
                JOIN CreatureTraits AS ct ON ct.TraitID = t.TraitID
                JOIN CreaturesStructured AS c ON c.CreatureKey = ct.CreatureKey
                WHERE ct.CreatureKey = ?
                GROUP BY t.TraitID, t.TName, t.TDescription
                ORDER BY t.TName, SourceCreature
                """,
                (copy_source_key,)
                
            )
        action_options = query_database(
                """
                SELECT ca.CreatureActionID, ca.CAName, ca.CADescription, c.CreatureName
                FROM CreatureActions AS ca
                JOIN CreaturesStructured AS c ON c.CreatureKey = ca.CreatureKey
                WHERE ca.CreatureKey = ?
                ORDER BY ca.CAName, c.CreatureName
                """,
                (copy_source_key,)
            )  
        copy_traits = [trait_id for trait_id, *_ in trait_options]
        copy_actions = [action_id for action_id, *_ in action_options]
    except duckdb.Error as error:
        st.error(f"Could not load stats from the selected creature: {error}")
        st.stop()

try:
    trait_options = query_database(
        """
        SELECT
            t.TraitID,
            t.TName,
            t.TDescription,
            min(c.CreatureName) AS SourceCreature
        FROM TraitsFiltered AS t
        JOIN CreatureTraits AS ct ON ct.TraitID = t.TraitID
        JOIN CreaturesStructured AS c ON c.CreatureKey = ct.CreatureKey
        GROUP BY t.TraitID, t.TName, t.TDescription
        ORDER BY t.TName, SourceCreature
        """,
        
    )
    action_options = query_database(
        """
        SELECT ca.CreatureActionID, ca.CAName, ca.CADescription, c.CreatureName
        FROM CreatureActions AS ca
        JOIN CreaturesStructured AS c ON c.CreatureKey = ca.CreatureKey
        ORDER BY ca.CAName, c.CreatureName
        """,
        
    )
except duckdb.Error as error:
    st.error(f"Could not search the trait/action library: {error}")
    st.stop()

trait_labels = {
    f"{trait_name} ({source_name})": [trait_id, trait_name, trait_description]
    for trait_id, trait_name, trait_description, source_name in trait_options
}
action_labels = {
    f"{action_name} ({source_name})": [action_id, action_name, action_description]
    for action_id, action_name, action_description, source_name in action_options
}
copy_trait_labels = [
    label for label, info in trait_labels.items() if info[0] in copy_traits
]
copy_action_labels = [
    label for label, info in action_labels.items() if info[0] in copy_actions
]
form_version = st.session_state.get("custom_form_version", 0)
widget_key = lambda field: f"custom_{field}_{form_version}"

selected_trait_labels = st.multiselect(
    "Traits to copy",
    options=list(trait_labels),
    default=copy_trait_labels,
    key=widget_key("selected_traits"),
)
selected_action_labels = st.multiselect(
    "Actions to copy",
    options=list(action_labels),
    default=copy_action_labels,
    key=widget_key("selected_actions"),
)

######custom form
with st.form(f"custom_creature_form_{form_version}"):
    st.subheader("Identity")
    identity_columns = st.columns(3)
    with identity_columns[0]:
        name = st.text_input("Creature name", key=widget_key("name"))
    with identity_columns[1]:
        creature_type = st.selectbox(
            "Creature type",
            creature_types,
            format_func=lambda row: row[1],
            index=next(
                (
                    index for index, row in enumerate(creature_types)
                    if row[0] == copy_stats.get("creature_type")
                ),
                0,
            ),
            key=widget_key("type"),
        )
    with identity_columns[2]:
        size = st.selectbox(
            "Size (Suggested Hit Die)",
            sizes,
            format_func=lambda row: f"{row[1]} ({row[2]})",
            index=next(
                (
                    index for index, row in enumerate(sizes)
                    if row[0] == copy_stats.get("size")
                ),
                0,
            ),
            key=widget_key("size"),
        )

    st.subheader("Combat")
    challenge_rating_options = sorted(
        set(
            CR_VALUES
            + (
                [copy_stats["challenge_rating"]]
                if copy_stats.get("challenge_rating") is not None
                else []
            )
        )
    )
    copied_challenge_rating = (
        copy_stats.get("challenge_rating")
        if copy_stats.get("challenge_rating") is not None
        else CR_VALUES[0]
    )
    combat_columns = st.columns(4)
    with combat_columns[0]:
        challenge_rating = st.selectbox(
            "Challenge rating",
            challenge_rating_options,
            index=challenge_rating_options.index(copied_challenge_rating),
            key=widget_key("cr"),
        )
    with combat_columns[1]:
        experience_points = st.number_input(
            "Experience points", min_value=0, step=25,
            value=copy_stats.get("experience_points") or 0,
            key=widget_key("xp"),
        )
    with combat_columns[2]:
        armour_class = st.number_input(
            "Armour class", min_value=0, max_value=127,
            value=copy_stats.get("armour_class") or 10, step=1,
            key=widget_key("ac"),
        )
    with combat_columns[3]:
        hit_points = st.number_input(
            "Hit points", min_value=0, max_value=32767,
            value=copy_stats.get("hit_points") or 1, step=1,
            key=widget_key("hp"),
        )
    armour_details = st.text_input(
        "Armour details",
        value=copy_stats.get("armour_details") or "",
        key=widget_key("armour_details"),
    )
    hit_dice = st.text_input(
        "Hit dice (for example, 4d8+8)",
        value=copy_stats.get("hit_dice") or "",
        key=widget_key("hit_dice"),
    )

    st.subheader("Ability scores")
    ability_columns = st.columns(6)
    ability_labels = ("Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma")
    ability_values = []
    for column, label, field in zip(
        ability_columns,
        ability_labels,
        ("str", "dex", "con", "int", "wis", "cha"),
    ):
        with column:
            ability_values.append(
                st.number_input(
                    label, min_value=1, max_value=30,
                    value=copy_stats.get(field) or 10, step=1,
                    key=widget_key(field),
                )
            )

    st.subheader("Movement")
    speed_columns = st.columns(6)
    speed_values = []
    for column, label, field in zip(
        speed_columns,
        ("Walk", "Fly", "Swim", "Climb", "Burrow", "Crawl"),
        ("walk", "fly", "swim", "climb", "burrow", "crawl"),
    ):
        with column:
            speed_values.append(
                st.number_input(
                    f"{label} speed (ft.)",
                    min_value=0,
                    max_value=32767,
                    value=copy_stats.get(field) or 0,
                    step=5,
                    key=widget_key(field),
                )
            )
    can_hover = st.checkbox(
        "Can hover",
        value=copy_stats.get("hover") or False,
        key=widget_key("hover"),
    )

    st.subheader("Senses")
    sense_columns = st.columns(6)
    sense_values = []
    for column, label, field in zip(
        sense_columns,
        (
            "Passive Perception",
            "Normal sight (ft.)",
            "Darkvision (ft.)",
            "Blindsight (ft.)",
            "Tremorsense (ft.)",
            "Truesight (ft.)",
        ),
        ("perception", "normal_sight", "darkvision", "blindsight", "tremorsense", "truesight"),
    ):
        with column:
            sense_values.append(
                st.number_input(
                    label,
                    min_value=0,
                    max_value=32767,
                    value=copy_stats.get(field) or 0,
                    step=1 if field == "perception" else 5,
                    key=widget_key(field),
                )
            )

    st.subheader("Saving throw proficiencies")
    save_columns = st.columns(3)
    selected_save_proficiencies = []
    for index, (label, column_name) in enumerate(SAVE_PROFICIENCIES):
        with save_columns[index % len(save_columns)]:
            if st.checkbox(
                label,
                value=column_name in copy_save_proficiencies,
                key=widget_key(f"save_{column_name}"),
            ):
                selected_save_proficiencies.append(column_name)

    st.subheader("Skill proficiencies")
    skill_columns = st.columns(3)
    selected_skill_proficiencies = []
    for index, (label, column_name) in enumerate(SKILL_PROFICIENCIES):
        with skill_columns[index % len(skill_columns)]:
            if st.checkbox(
                label,
                value=column_name in copy_skill_proficiencies,
                key=widget_key(f"skill_{column_name}"),
            ):
                selected_skill_proficiencies.append(column_name)

    st.subheader("Languages and defenses")
    language_labels = {label: key for key, label in languages}
    selected_languages = st.multiselect(
        "Languages",
        options=list(language_labels),
        default=copy_languages,
        key=widget_key("languages"),
    )
    environment_labels = {label: (key, label) for key, label in environments}
    selected_environments = st.multiselect(
        "Environments",
        options=list(environment_labels),
        default=copy_environments,
        key=widget_key("environments"),
    )
    condition_labels = {label: key for key, label in conditions}
    selected_conditions = st.multiselect(
        "Condition immunities",
        options=list(condition_labels),
        default=copy_conditions,
        key=widget_key("condition_immunities"),
    )
    damage_labels = {
        f"{damage_name} - {relationship.title()}": (damage_key, relationship)
        for damage_key, damage_name in damage_types
        for relationship in ("immunity", "resistance", "vulnerability")
    }
    selected_damage_labels = st.multiselect(
        "Damage relationships",
        options=list(damage_labels),
        default=copy_damage_relationships,
        key=widget_key("damage_relationships"),
    )
    st.subheader("Traits")
    if selected_trait_labels:
        for label in selected_trait_labels:
            _, trait_name, description = trait_labels[label]
            st.markdown(f"**{trait_name}.** {description}")
    else:
        st.markdown("--")

    st.subheader("Actions")
    if selected_action_labels:
        for label in selected_action_labels:
            _, action_name, description = action_labels[label]
            st.markdown(f"**{action_name}.** {description}")
    else:
        st.markdown("--")

    submitted = st.form_submit_button("Create creature", type="primary")

if submitted:
    if not name.strip():
        st.error("Enter a creature name.")
    else:
        try:
            created_key = save_creature(
                name=name,
                creature_type=creature_type[0],
                size=size[0],
                challenge_rating=float(challenge_rating),
                experience_points=int(experience_points),
                armour_class=int(armour_class),
                armour_details=armour_details,
                hit_points=int(hit_points),
                hit_dice=hit_dice,
                ability_scores=tuple(int(value) for value in ability_values),
                speeds=tuple(int(value) for value in speed_values),
                can_hover=can_hover,
                senses=tuple(int(value) for value in sense_values),
                language_keys=[language_labels[label] for label in selected_languages],
                environments=[
                    environment_labels[label] for label in selected_environments
                ],
                condition_keys=[
                    condition_labels[label] for label in selected_conditions
                ],
                damage_relationships=[
                    damage_labels[label] for label in selected_damage_labels
                ],
                skill_proficiencies=selected_skill_proficiencies,
                save_proficiencies=selected_save_proficiencies,
                trait_ids=[trait_labels[label][0] for label in selected_trait_labels],
                action_ids=[action_labels[label][0] for label in selected_action_labels],
            )
        except duckdb.Error as error:
            st.error(f"Could not save the custom creature: {error}")
        else:
            st.session_state["created_creature_key"] = created_key
            st.session_state["custom_form_version"] = form_version + 1
            st.rerun()

if created_key := st.session_state.get("created_creature_key"):
    st.success(f"Created custom creature with key `{created_key}`.")