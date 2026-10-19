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
DICE    = re.compile(
    r"(?:(?P<avg>\d+)\s*)?\(\s*(?P<n>\d+)d(?P<d>\d+)"
    r"(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\s*\)\s+"
    r"(?P<type>[a-z]+)\s+damage(?P<tail>[^.]{0,40})", re.I)
FLAT    = re.compile(r"(?<![\d(/])\b(?P<avg>\d+)\s+(?P<type>[a-z]+)\s+damage", re.I)

def parse_attack(desc: str) -> dict:
    text = desc.translate(NORM)
    out = {"status": "unparsed", "damage": []}

    h = HEADER.search(text)
    if h:
        out["attack_type"] = h["atk_type"].upper()
        out["melee"]  = "melee"  in (h["range_kind"] + (h["range_kind2"] or "")).lower()
        out["ranged"] = "ranged" in (h["range_kind"] + (h["range_kind2"] or "")).lower()
        out["to_hit"] = int(h["to_hit"].replace(" ", ""))
        if m := REACH.search(text):
            out["reach"] = int(m[1])
        if m := RANGE.search(text):
            out["range_normal"] = int(m[1])
            out["range_long"] = int(m[2]) if m[2] else None

    # Only look for damage after "Hit:" so we skip rider text before it
    hit_part = text.split("Hit:", 1)[1] if "Hit:" in text else text

    for m in DICE.finditer(hit_part):
        bonus = int(m["bonus"] or 0) * (-1 if m["sign"] == "-" else 1)
        out["damage"].append({
            "die_count": int(m["n"]), "die_size": int(m["d"]), "bonus": bonus,
            "type": m["type"].lower(), "avg_stated": int(m["avg"]) if m["avg"] else None,
            "conditional": bool(re.search(r"\bif\b", m["tail"], re.I)),
        })

    if not out["damage"]:                       # flat damage, e.g. "Hit: 1 piercing damage"
        for m in FLAT.finditer(hit_part):
            out["damage"].append({"die_count": 0, "die_size": 0, "bonus": int(m["avg"]),
                                  "type": m["type"].lower(), "avg_stated": int(m["avg"]),
                                  "conditional": False})

    if out["damage"]:
        out["status"] = "parsed" if validate(out["damage"]) else "check"
    return out

def validate(damage_list) -> bool:
    for d in damage_list:
        if d["avg_stated"] is None or d["die_count"] == 0:
            continue
        calc = math.floor(d["die_count"] * (d["die_size"] + 1) / 2) + d["bonus"]
        if calc != d["avg_stated"]:
            return False
    return True

def main():
    DUCKDB_DIR = ROOT_DIR/"duckdb"/"CreatureCreator.duckdb"
    DUCKDB_DIR.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DUCKDB_DIR)) #(SELECT unnest(attacks, max_depth := 2) FROM Actions) WHERE name = \'Light Crossbow attack\' AND damage_die_type = NULL
    test = con.sql('SELECT "desc" FROM Actions WHERE NOT attacks = []').fetchall()
    #print(test)
    #print(parse_attack(test[0]))
    for desc in test:
        print(desc[0])
        print(parse_attack(desc[0]))
    
if __name__ == "__main__":
    main()