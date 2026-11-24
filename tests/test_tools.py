from body.agent import tool_get_build

def test_fuzzy_typo():
    # typo "furna" harus dikoreksi ke Furina via rapidfuzz
    b = tool_get_build("furna")
    assert b.get("name") == "Furina"

def test_unknown_lists_available():
    b = tool_get_build("Nggak Ada")
    assert b["error"] == "unknown_character"
    assert "available" in b and isinstance(b["available"], list)
