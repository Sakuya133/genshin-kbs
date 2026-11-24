from brain.reasoner import get_build, list_characters

def test_list():
    assert {"Furina", "Xingqiu", "Zhongli"} <= set(list_characters())

def test_furina_scales_hp():
    b = get_build("Furina")
    assert "HP" in b["scales_with"] and b["is_hp_scaler"]

def test_furina_has_domain():
    assert len(get_build("Furina")["domains"]) > 0

def test_xingqiu_domain_empty():
    assert get_build("Xingqiu")["domains"] == []

def test_unknown_character():
    assert get_build("Nggak Ada")["error"] == "unknown_character"
