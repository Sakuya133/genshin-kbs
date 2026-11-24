import os
from owlready2 import *

_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kb", "genshin.owl"))
_onto = get_ontology("file://" + _PATH).load()

def list_characters():
    return sorted(c.name for c in _onto.Character.instances())

def get_build(char: str) -> dict:
    c = _onto[char]
    if c is None or not isinstance(c, _onto.Character):
        return {"error": "unknown_character", "name": char}
    return {
        "name": c.name,
        "element": c.hasElement.name if c.hasElement else None,
        "weapon": c.hasWeapon.name if c.hasWeapon else None,
        "roles": [r.name for r in c.hasRole],
        "scales_with": [s.name for s in c.scalesWith],
        "sets": [s.name for s in c.recommendsSet],
        "domains": [d.name for d in c.recommendedDomain],
        "is_hp_scaler": any(t.name == "HPScaler" for t in c.is_a),
    }
