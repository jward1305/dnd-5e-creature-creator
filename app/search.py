from pathlib import Path
from typing import Any

import duckdb
import pandas as pd
import streamlit as st
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(1, str(Path(__file__).resolve().parent.parent))

from config import DUCKDB_DIR
from database import query_database


RELATIONSHIP_CHOICES: tuple[tuple[str, str], ...] = (
    ("immunity", "Immunity"),
    ("resistance", "Resistance"),
    ("vulnerability", "Vulnerability"),
)

CR_VALUES = [0, 0.125, 0.25, 0.5, 
             1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 
             11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30]

#Gets the possible values that can be filtered by
@st.cache_data
def get_filter_options() -> dict[str, list[str]]:
    option_queries = {
        "creature_types": """
            SELECT CTKey
            FROM CreatureTypesStructured
            ORDER BY CTKey
        """,
        "creature_sizes": """
            SELECT SKey
            FROM SizesStructured
            ORDER BY SKey
        """,
        "environments": """
            SELECT EKey, EName
            FROM EnvironmentsStructured
            ORDER BY EKey
        """,
        "conditions": """
            SELECT CName
            FROM ConditionsStructured
            ORDER BY CName
        """,
        "damage_types": """
            SELECT DTKey
            FROM DamageTypesStructured
            ORDER BY DTKey
        """,
    }
    options = {
        key: [row[0] for row in query_database(query)]
        for key, query in option_queries.items()
        if key != "environments"
    }
    environments = query_database(option_queries["environments"])
    options["environments"] = [row[1] for row in environments]
    options["environments_keys"] = [row[0] for row in environments]
    return options

######Search Function

def find_creatures(
    search_text: str,
    creature_types: list[str],
    creature_sizes: list[str],
    challenge_rating: tuple[float, float],
    environments: list[str],
    conditions: list[str],
    damage_filters: list[tuple[str, str]],
    custom_creature_filter: str = "Include",
) -> list[tuple[Any, ...]]:
    predicates = ["TRUE"]
    parameters: list[Any] = []

    if custom_creature_filter == "Exclude":
        predicates.append("c.isCustom = FALSE")
    elif custom_creature_filter == "Only":
        predicates.append("c.isCustom = TRUE")

    if search_text.strip():
        predicates.append("contains(lower(c.CreatureName), lower(?))")
        parameters.append(search_text.strip())

    def add_in_filter(expression: str, values: list[str]) -> None:
        if values:
            placeholders = ", ".join("?" for _ in values)
            predicates.append(f"{expression} IN ({placeholders})")
            parameters.extend(values)

    add_in_filter("c.CreatureType", creature_types)
    add_in_filter("c.CreatureSize", creature_sizes)

    predicates.append("c.Challenge_Rating BETWEEN ? AND ?")
    parameters.extend(challenge_rating)

    def add_link_filter(
        table: str,
        alias: str,
        key_column: str,
        lookup_table: str,
        lookup_key: str,
        lookup_name: str,
        selected_names: list[str],
    ) -> None:
        if not selected_names:
            return
        placeholders = ", ".join("?" for _ in selected_names)
        predicates.append(
            f"""EXISTS (
                SELECT 1
                FROM {table} AS {alias}
                JOIN {lookup_table} AS lookup
                    ON lookup.{lookup_key} = {alias}.{key_column}
                WHERE {alias}.CreatureKey = c.CreatureKey
                  AND lookup.{lookup_name} IN ({placeholders})
            )"""
        )
        parameters.extend(selected_names)

    add_link_filter(
        "CreatureEnvironments", "ce", "EKey",
        "EnvironmentsStructured", "EKey", "EName", environments,
    )
    add_link_filter(
        "CreatureConditionImmunities", "ci", "CKey",
        "ConditionsStructured", "CKey", "CName", conditions,
    )

    if damage_filters:
        print(damage_filters)
        selected_damage_predicates = []
        for damage_type_key, relationship in damage_filters:
            selected_damage_predicates.append(
                "(cdr.DTKey = ? AND cdr.Relationship = ?)"
            )
            parameters.extend((damage_type_key, relationship))
        predicates.append(
            "EXISTS (SELECT 1 FROM CreatureDamageRelationships AS cdr "
            "WHERE cdr.CreatureKey = c.CreatureKey AND ("
            + " OR ".join(selected_damage_predicates)
            + ")"
            + ")"
        )
        #print(predicates)
        #print(parameters)

    query = f"""
        SELECT
            c.CreatureName AS Name,
            c.CreatureType AS Type,
            c.CreatureSize AS Size,
            c.Challenge_Rating AS CR,
            c.Armour_Class AS AC,
            c.Hit_Points AS HP,
            c.CreatureKey
        FROM CreaturesStructured AS c
        WHERE {" AND ".join(predicates)}
        ORDER BY c.CreatureName
    """
    #print(query)
    return query_database(query, tuple(parameters))

###############Details###################

def get_creature_details(creature_key: str) -> dict[str, Any] | None:
    connection = duckdb.connect(str(DUCKDB_DIR), read_only=True)
    try:
        creature = connection.execute(
            """
            SELECT
                CreatureName, CreatureType, CreatureSize, Challenge_Rating,
                Experience_Points, Proficiency_Bonus, Armour_Class, Armour_Details,
                Hit_Points, Hit_Dice, Str, Dex, Con, Int, Wis, Cha,
                Walk_Speed, Fly_Speed, Swim_Speed, Climb_Speed, Burrow_Speed,
                Crawl_Speed, canHover, Passive_Perception, Normal_Sight_Range,
                Darkvision_Range, Blindsight_Range, Tremorsense_Range,
                True_Sight_Range, Languages_Display, Damage_Immunities_Display,
                Damage_Resistances_Display, Damage_Vulnerabilities_Display
            FROM CreaturesStructured
            WHERE CreatureKey = ?
            """,
            [creature_key],
        ).fetchone()
        if creature is None:
            return None

        details: dict[str, Any] = {"creature": creature}
        skill_proficiencies = connection.execute(
            """
            SELECT
                Athletics_Prof, Acrobatics_Prof, SleightOfHand_Prof,
                Stealth_Prof, Arcana_Prof, History_Prof, Investigation_Prof,
                Nature_Prof, Religion_Prof, AnimalHandling_Prof, Insight_Prof,
                Medicine_Prof, Perception_Prof, Survival_Prof, Deception_Prof,
                Intimidation_Prof, Performance_Prof, Persuasion_Prof
            FROM CreatureSkillProficiencies
            WHERE CreatureKey = ?
            """,
            [creature_key],
        ).fetchone()
        save_proficiencies = connection.execute(
            """
            SELECT Str_Prof, Dex_Prof, Con_Prof, Int_Prof, Wis_Prof, Cha_Prof
            FROM CreatureSaveProficiencies
            WHERE CreatureKey = ?
            """,
            [creature_key],
        ).fetchone()

        ability_scores = {
            "strength": creature[10],
            "dexterity": creature[11],
            "constitution": creature[12],
            "intelligence": creature[13],
            "wisdom": creature[14],
            "charisma": creature[15],
        }
        skill_definitions = (
            ("Athletics", "strength"),
            ("Acrobatics", "dexterity"),
            ("Sleight of Hand", "dexterity"),
            ("Stealth", "dexterity"),
            ("Arcana", "intelligence"),
            ("History", "intelligence"),
            ("Investigation", "intelligence"),
            ("Nature", "intelligence"),
            ("Religion", "intelligence"),
            ("Animal Handling", "wisdom"),
            ("Insight", "wisdom"),
            ("Medicine", "wisdom"),
            ("Perception", "wisdom"),
            ("Survival", "wisdom"),
            ("Deception", "charisma"),
            ("Intimidation", "charisma"),
            ("Performance", "charisma"),
            ("Persuasion", "charisma"),
        )
        skill_levels = skill_proficiencies or (0,) * len(skill_definitions)
        details["skills"] = [
            (
                skill_name,
                (ability_scores[ability] - 10) // 2
                + proficiency_level * creature[5],
            )
            for (skill_name, ability), proficiency_level
            in zip(skill_definitions, skill_levels)
            if proficiency_level is not None and proficiency_level > 0
        ]

        save_definitions = (
            ("Strength", "strength"),
            ("Dexterity", "dexterity"),
            ("Constitution", "constitution"),
            ("Intelligence", "intelligence"),
            ("Wisdom", "wisdom"),
            ("Charisma", "charisma"),
        )
        save_levels = save_proficiencies or (0,) * len(save_definitions)
        details["saving_throws"] = [
            (
                ability_name,
                (ability_scores[ability] - 10) // 2
                + proficiency_level * creature[5],
            )
            for (ability_name, ability), proficiency_level
            in zip(save_definitions, save_levels)
            if proficiency_level is not None and proficiency_level > 0
        ]

        details["languages"] = connection.execute(
                    """
                    SELECT l.LName
                    FROM CreatureLanguages AS cl
                    JOIN LanguagesStructured AS l ON l.LKey = cl.LKey
                    WHERE cl.CreatureKey = ?
                    ORDER BY l.LName
                    """,
                    [creature_key],
                ).fetchall()
        details["environments"] = connection.execute(
            """
            SELECT e.EName
            FROM CreatureEnvironments AS ce
            JOIN EnvironmentsStructured AS e ON e.EKey = ce.EKey
            WHERE ce.CreatureKey = ?
            ORDER BY e.EName
            """,
            [creature_key],
        ).fetchall()
        details["condition_immunities"] = connection.execute(
            """
            SELECT c.CName
            FROM CreatureConditionImmunities AS ci
            JOIN ConditionsStructured AS c ON c.CKey = ci.CKey
            WHERE ci.CreatureKey = ?
            ORDER BY c.CName
            """,
            [creature_key],
        ).fetchall()
        details["damage_relationships"] = connection.execute(
            """
            SELECT d.DTName, cdr.Relationship
            FROM CreatureDamageRelationships AS cdr
            JOIN DamageTypesStructured AS d ON d.DTKey = cdr.DTKey
            WHERE cdr.CreatureKey = ?
            ORDER BY cdr.Relationship, d.DTName
            """,
            [creature_key],
        ).fetchall()
        details["traits"] = connection.execute(
            """
            SELECT t.TName, t.TDescription
            FROM CreatureTraits AS ct
            JOIN TraitsFiltered AS t ON t.TraitID = ct.TraitID
            WHERE ct.CreatureKey = ?
            ORDER BY t.TName
            """,
            [creature_key],
        ).fetchall()
        details["actions"] = connection.execute(
            """
            SELECT
                ca.CreatureActionID, ca.CAName, ca.CADescription,
                a.ToHit, a.Reach, a.ARange, a.ALongRange,
                a.TargetCreatureOnly, a.DamageDieCount, a.DamageDieType,
                a.DamageBonus, a.DamageType, a.ExtraDamageDieCount,
                a.ExtraDamageDieType, a.ExtraDamageBonus, a.ExtraDamageType
            FROM CreatureActions AS ca
            LEFT JOIN Attacks AS a ON a.CreatureActionID = ca.CreatureActionID
            WHERE ca.CreatureKey = ?
            ORDER BY ca.CAName, a.AttackID
            """,
            [creature_key],
        ).fetchall()
        return details
    finally:
        connection.close()

######Render creature details

def render_creature_details(details: dict[str, Any]) -> None:
    creature = details["creature"]
    (
        name, creature_type, size, challenge_rating, experience_points,
        proficiency_bonus, armour_class, armour_details, hit_points, hit_dice,
        strength, dexterity, constitution, intelligence, wisdom, charisma,
        walk_speed, fly_speed, swim_speed, climb_speed, burrow_speed,
        crawl_speed, can_hover, passive_perception, normal_sight, darkvision,
        blindsight, tremorsense, truesight, languages, damage_immunities,
        damage_resistances, damage_vulnerabilities,
    ) = creature

    st.title(name)
    st.caption(f"{size.title()} {creature_type.title()} · CR {challenge_rating:g}")

    stat_columns = st.columns(5)
    stat_columns[0].metric("Armor Class", armour_class)
    stat_columns[1].metric("Hit Points", hit_points)
    stat_columns[2].metric("Hit Dice", hit_dice or "--")
    stat_columns[3].metric("Proficiency Bonus", f"+{proficiency_bonus}")
    stat_columns[4].metric("Experience", experience_points)
    st.write(armour_details or " ")

    st.subheader("Ability scores")
    ability_columns = st.columns(6)
    for column, label, score in zip(
        ability_columns,
        ("STR", "DEX", "CON", "INT", "WIS", "CHA"),
        (strength, dexterity, constitution, intelligence, wisdom, charisma),
    ):
        column.metric(label, score)

    st.subheader("Saving throws")
    if details["saving_throws"]:
        st.write(", ".join(
            f"{ability} {modifier:+}"
            for ability, modifier in details["saving_throws"]
        ))
    else:
        st.write("--")

    st.subheader("Skills")
    if details["skills"]:
        st.write(", ".join(
            f"{skill} {modifier:+}"
            for skill, modifier in details["skills"]
        ))
    else:
        st.write("--")

    left, right = st.columns(2)
    with left:
        st.subheader("Movement")
        speeds = [
            (label, value)
            for label, value in (
                ("Walk", walk_speed),
                ("Fly", fly_speed),
                ("Swim", swim_speed),
                ("Climb", climb_speed),
                ("Burrow", burrow_speed),
                ("Crawl", crawl_speed),
            )
            if value != 0
        ]
        if speeds:
            st.write(", ".join(f"{label} {value} ft." for label, value in speeds))
        if can_hover:
            st.write("Can hover")
    with right:
        st.subheader("Senses")
        senses = [
            (label, value)
            for label, value in (
                ("Normal Sight", normal_sight),
                ("Darkvision", darkvision),
                ("Blindsight", blindsight),
                ("Tremorsense", tremorsense),
                ("Truesight", truesight),
                ("Passive Perception", passive_perception),
            )
        ]
        
        sensesFull = ""
        blind = False
        for label, value in senses:
            if label != "Normal Sight" and (value is not None and value != 0):
                if label == "Blindsight" and blind:
                    sensesFull += f"{label} {value} ft. (blind beyond this radius), "
                elif label == "Passive Perception": 
                    sensesFull += f"{label} {value}"
                else:
                    sensesFull += f"{label} {value} ft., "
            elif label == "Normal Sight" and (value is None or value == 0):
                blind = True
        st.write(sensesFull or "--")
    st.subheader("Languages")    
    if details["languages"]:
        st.write(", ".join(row[0] for row in details["languages"]))
    else:
        st.write("--")


    relationship_labels = {
        "immunity": "Immunities",
        "resistance": "Resistances",
        "vulnerability": "Vulnerabilities",
    }
    
    relationship_groups = {
        relationship: [
            damage_type
            for damage_type, row_relationship in details["damage_relationships"]
            if row_relationship == relationship
        ]
        for relationship in relationship_labels
    }
    condition_names = [row[0] for row in details["condition_immunities"]]
    if damage_immunities or damage_resistances or damage_vulnerabilities or condition_names:
        st.subheader("Defenses")
        for relationship, label in relationship_labels.items():
            values = relationship_groups[relationship]
            if values:
                st.write(f"**{label}:** {', '.join(values)}")
        if condition_names:
            st.write(f"**Condition immunities:** {', '.join(condition_names)}")
    elif not damage_immunities and not damage_resistances and not damage_vulnerabilities:
        st.subheader("Defenses")
        st.write("--")

    if details["environments"]:
        st.subheader("Environments")
        st.write(", ".join(row[0] for row in details["environments"]))

    if details["traits"]:
        st.subheader("Traits")
        for trait_name, description in details["traits"]:
            st.markdown(f"**{trait_name}.** {description}")

    if details["actions"]:
        st.subheader("Actions")
        for action in details["actions"]:
            (
                _action_id, action_name, description, to_hit, reach, attack_range,
                long_range, target_creature_only, die_count, die_type, damage_bonus,
                damage_type, extra_die_count, extra_die_type, extra_damage_bonus,
                extra_damage_type,
            ) = action
            st.markdown(f"**{action_name}.** {description}")
            if to_hit is not None:
                st.caption(f"{to_hit:+} to hit")
            attack_data = {
                "Reach": f"{reach} ft." if reach is not None else None,
                "Range": (
                    f"{attack_range}/{long_range} ft."
                    if long_range is not None
                    else f"{attack_range} ft."
                    if attack_range is not None
                    else None
                ),
                "Damage": (
                    f"{die_count}{die_type or ''} + {damage_bonus or 0} {damage_type or ''}".strip()
                    if die_count is not None or damage_type
                    else None
                ),
                "Extra damage": (
                    f"{extra_die_count}{extra_die_type or ''} + "
                    f"{extra_damage_bonus or 0} {extra_damage_type or ''}".strip()
                    if extra_die_count is not None or extra_damage_type
                    else None
                ),
            }
            summary = [
                f"{label}: {value}"
                for label, value in attack_data.items()
                if value is not None
            ]
            if summary:
                st.caption(" · ".join(summary))

if not DUCKDB_DIR.is_file():
    st.error(f"Database not found at `{DUCKDB_DIR}`. Build the database before starting the app.")
    st.stop()

st.title("DnD Creature Creator")
st.caption("Find creatures by name, statistics, and linked traits.")

try:
    options = get_filter_options()
    rating_bounds = query_database(
        "SELECT min(Challenge_Rating), max(Challenge_Rating) FROM CreaturesStructured"
    )[0]
except duckdb.Error as error:
    st.error(f"Could not load creature data from the database: {error}")
    st.stop()

if rating_bounds[0] is None or rating_bounds[1] is None:
    st.info("The creature table is empty. Populate the database to search creatures.")
    st.stop()

with st.sidebar:
    st.header("Filters")
    search_text = st.text_input("Creature name")
    creature_types = st.multiselect(
        "Creature type", options["creature_types"], format_func=str.title
    )
    creature_sizes = st.multiselect(
        "Size", options["creature_sizes"], format_func=str.title
    )
    challenge_rating = st.select_slider(
        "Challenge rating",
        options=CR_VALUES,
        value=(CR_VALUES[0], CR_VALUES[-1]),
        format_func=lambda cr: f"{cr:g}",
    )
    environments = st.multiselect(
        "Environments", options["environments"], format_func=str.title
    )
    conditions = st.multiselect(
        "Condition immunities", options["conditions"], format_func=str.title
    )
    custom_creature_filter = st.selectbox(
        "Custom creatures",
        options=("Include", "Exclude", "Only"),
    )
    damage_filter_options: dict[str, tuple[str, str]] = {}
    for damage_type in options["damage_types"]:
        for relationship_key, relationship_label in RELATIONSHIP_CHOICES:
            damage_filter_options[
                f"{damage_type.capitalize()} - {relationship_label}"
            ] = (damage_type, relationship_key)
    selected_damage_filters = st.multiselect(
        "Damage type / relationship",
        options=list(damage_filter_options),
    )

damage_filters = [
    damage_filter_options[label] for label in selected_damage_filters
]

try:
    creature_rows = find_creatures(
        search_text,
        creature_types,
        creature_sizes,
        challenge_rating,
        environments,
        conditions,
        damage_filters,
        custom_creature_filter,
    )
except duckdb.Error as error:
    st.error(f"Could not search creatures: {error}")
    st.stop()

if "results_table_version" not in st.session_state:
    st.session_state["results_table_version"] = 0

selected_creature_key = st.session_state.get("selected_creature_key")
if selected_creature_key:
    if st.button("← Back to results"):
        del st.session_state["selected_creature_key"]
        st.session_state["results_table_version"] += 1
        st.rerun()
    try:
        creature_details = get_creature_details(selected_creature_key)
    except duckdb.Error as error:
        st.error(f"Could not load creature details: {error}")
        st.stop()
    if creature_details is None:
        st.error("That creature could not be found in the database.")
        st.stop()
    render_creature_details(creature_details)
    st.stop()

st.subheader(f"{len(creature_rows)} creature(s)")
st.caption("Click a creature row to view its details.")
results = pd.DataFrame(
    creature_rows,
    columns=["Name", "Type", "Size", "CR", "AC", "HP", "CreatureKey"],
)
results["Type"] = results["Type"].str.title()
results["Size"] = results["Size"].str.title()

selection = st.dataframe(
    results,
    column_order=["Name", "Type", "Size", "CR", "AC", "HP"],
    column_config={
        "CR": st.column_config.NumberColumn("CR", format="%.3g"),
    },
    hide_index=True,
    width="stretch",
    key=f"creature_results_{st.session_state['results_table_version']}",
    on_select="rerun",
    selection_mode="single-row",
)

if selection.selection.rows:
    selected_row = results.iloc[selection.selection.rows[0]]
    st.session_state["selected_creature_key"] = selected_row["CreatureKey"]
    st.rerun()