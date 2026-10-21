import re
import math
import duckdb
from config import ROOT_DIR

NORM = str.maketrans({"–": "-", "−": "-", "—": "-"})   # unicode minus signs

HEADER = re.compile(
    r"(?P<range_kind>Melee|Ranged)(?: or (?P<range_kind2>Melee|Ranged))?\s+"
    r"(?P<atk_type>Weapon|Spell)\s+Attack:\s*(?P<to_hit>[+-]\s*\d+)\s+to hit",
    re.I)
REACH   = re.compile(r"reach\s+(\d+)\s*ft", re.I)
RANGE   = re.compile(r"range\s+(\d+)(?:\s*/\s*(\d+))?\s*ft", re.I)
TARGET  = re.compile(r"one(?:\s+[a-z]+)*\s+(?P<target_kind>creature|target)", re.I)
TWO_HANDED = re.compile(r"\btwo[- ]hand(?:s|ed)?\b", re.I)
CONDITION  = re.compile(r"\bif\b", re.I)
DICE = re.compile(
    r"(?:(?P<avg>\d+)\s*)?\(\s*(?P<n>\d+)d(?P<d>\d+)"
    r"(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\s*\)\s+"
    r"(?P<type>[a-z]+)\s+damage", re.I)
FLAT    = re.compile(r"(?<![\d(/])\b(?P<avg>\d+)\s+(?P<type>[a-z]+)\s+damage", re.I)

def parse_attack(desc: str) -> dict:
    text = desc.translate(NORM)
    out = {
        "attack_type": None,
        "melee": False,
        "ranged": False,
        "to_hit": None,
        "reach": None,
        "range_normal": None,
        "range_long": None,
        "target_only_creatures": None,
        "damage": [],
    }

    h = HEADER.search(text)
    if h:
        kinds = (h["range_kind"] + (h["range_kind2"] or "")).lower()
        out["attack_type"] = h["atk_type"].upper()
        out["melee"] = "melee" in kinds
        out["ranged"] = "ranged" in kinds
        out["to_hit"] = int(h["to_hit"].replace(" ", ""))

        if out["melee"] and (m := REACH.search(text)):
            out["reach"] = int(m[1])
        if out["ranged"] and (m := RANGE.search(text)):
            out["range_normal"] = int(m[1])
            out["range_long"] = int(m[2]) if m[2] else None

        out["to_hit"] = int(h["to_hit"].replace(" ", ""))
        if m := REACH.search(text):
            out["reach"] = int(m[1])
        if m := RANGE.search(text):
            out["range_normal"] = int(m[1])
            out["range_long"] = int(m[2]) if m[2] else None
        if (m := TARGET.search(text)["target_kind"]) == "target":
            out["target_only_creatures"] = False
        elif (m := TARGET.search(text)["target_kind"]) == "creature":
            out["target_only_creatures"] = True

    # Only look for damage after "Hit:" so we skip rider text before it
    hit_part = text.split("Hit:", 1)[1] if "Hit:" in text else text

    matches = list(DICE.finditer(hit_part))
    for i, m in enumerate(matches):
        # Text between this clause and the next one (or the end of the sentence)
        nxt = matches[i + 1].start() if i + 1 < len(matches) else len(hit_part)
        between = hit_part[m.end():nxt].split(".")[0]

        conditional = bool(CONDITION.search(between))
        bonus = int(m["bonus"] or 0) * (-1 if m["sign"] == "-" else 1)
        if out["damage"] == [] or conditional:
            extra = False
        else:
            extra = True
        out["damage"].append({
            "die_count": int(m["n"]), 
            "die_size": "D" + m["d"], 
            "bonus": bonus,
            "type": m["type"].lower(),
            "avg_stated": int(m["avg"]) if m["avg"] else None,
            "conditional": conditional,
            "handedness": "two_handed" if conditional and TWO_HANDED.search(between) else None,
            "extra": extra,
        })

    for i, d in enumerate(out["damage"]):
        if d["handedness"] == "two_handed" and i > 0 and not out["damage"][i - 1]["conditional"]:
            out["damage"][i - 1]["handedness"] = "one_handed"

    if not out["damage"]:                       # flat damage fallback
        for m in FLAT.finditer(hit_part):
            out["damage"].append({"die_count": 0, "die_size": 0, "bonus": int(m["avg"]),
                                  "type": m["type"].lower(), "avg_stated": int(m["avg"]),
                                  "conditional": False, "handedness": None, "extra": False})
    return out

def main():
    DUCKDB_DIR = ROOT_DIR/"duckdb"/"CreatureCreator.duckdb"
    DUCKDB_DIR.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DUCKDB_DIR))
    
    con.execute(
                """
                INSERT OR IGNORE INTO CreatureActions (CreatureActionID, CreatureKey, CAName, CADescription)
                SELECT ActionID, CreatureKey, name, "desc", attacks FROM Actions
                """
            )
    
    actions_to_parse = con.execute("""SELECT ActionID, name, "desc" FROM Actions WHERE attacks <> []""").fetchall()
    parsed_attacks = []
    for id, name, desc in actions_to_parse: 
        attackdata = parse_attack(desc)
        
        die_count, die_size, damage_bonus, damage_type = None, None, None, None
        extra_die_count, extra_die_size, extra_damage_bonus, extra_damage_type = None, None, None, None
        
        for attackVar in attackdata['damage']:
            
            if attackVar['extra'] == False:
                if attackVar['conditional'] == False:
                    die_count = attackVar['die_count']
                    die_size = attackVar['die_size']
                    damage_bonus = attackVar['bonus']
                    damage_type = attackVar['type']
                elif attackVar['conditional'] == True and attackVar['handedness'] == 'two_handed':
                    die_count = attackVar['die_count']
                    die_size = attackVar['die_size']
                    damage_bonus = attackVar['bonus']
                    damage_type = attackVar['type']
            elif attackVar['extra'] == True:
                extra_die_count = attackVar['die_count']
                extra_die_size = attackVar['die_size']
                extra_damage_bonus = attackVar['bonus']
                extra_damage_type = attackVar['type']
        
        attack_names = []       
        if attackdata['melee'] and attackdata['ranged']:
            attack_names.append(f"{name} + Melee Attack")
            attack_names.append(f"{name} + Ranged Attack")
        else:
            attack_names.append(f"{name}")

        for attack_name in attack_names:
            parsed_attacks.append((
                        id, 
                        attack_name,
                        attackdata['to_hit'], 
                        attackdata['reach'], 
                        attackdata['range_normal'], 
                        attackdata['range_long'], 
                        attackdata['target_only_creatures'], 
                        die_count, 
                        die_size, 
                        damage_bonus, 
                        damage_type, 
                        extra_die_count, 
                        extra_die_size, 
                        extra_damage_bonus, 
                        extra_damage_type
                        ))

    attack_query = """
                        INSERT INTO Attacks (
                            CreatureActionID, AName, ToHit, Reach, ARange, ALongRange,
                            TargetCreatureOnly, DamageDieCount, DamageDieType, DamageBonus,
                            DamageType, ExtraDamageDieCount, ExtraDamageDieType,
                            ExtraDamageBonus, ExtraDamageType
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """   
    con.executemany(attack_query, parsed_attacks)
    con.table("CreatureActions").show()
    con.table("Attacks").show()
    con.close()

if __name__ == "__main__":
    main()