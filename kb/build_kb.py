import os
from owlready2 import *

onto = get_ontology("http://example.org/genshin.owl")

with onto:
    # --- TBox: kelas ---
    class Character(Thing): pass
    class Role(Thing): pass
    class Element(Thing): pass
    class WeaponType(Thing): pass
    class Stat(Thing): pass
    class ArtifactSet(Thing): pass

    # --- TBox: property ---
    class hasElement(ObjectProperty, FunctionalProperty):
        domain = [Character]; range = [Element]
    class hasWeapon(ObjectProperty, FunctionalProperty):
        domain = [Character]; range = [WeaponType]
    class hasRole(ObjectProperty):
        domain = [Character]; range = [Role]
    class scalesWith(ObjectProperty):
        domain = [Character]; range = [Stat]
    class recommendsSet(ObjectProperty):
        domain = [Character]; range = [ArtifactSet]
    class hasShield(DataProperty, FunctionalProperty):
        domain = [Character]; range = [bool]

    # --- ABox: individu referensi ---
    HP, ATK, DEF, EM, ER = Stat("HP"), Stat("ATK"), Stat("DEF"), Stat("EM"), Stat("ER")
    Hydro, Geo = Element("Hydro"), Element("Geo")
    Sword, Polearm = WeaponType("Sword"), WeaponType("Polearm")
    SubDPS, Support = Role("SubDPS"), Role("Support")
    GoldenTroupe = ArtifactSet("GoldenTroupe")
    Tenacity = ArtifactSet("TenacityOfTheMillelith")
    SeveredFate = ArtifactSet("EmblemOfSeveredFate")
    Noblesse = ArtifactSet("NoblesseOblige")

    # --- Defined class: diturunkan reasoner ---
    class HPScaler(Character):
        equivalent_to = [Character & scalesWith.value(HP)]

    # --- Karakter (hanya fakta yang disebut sumber) ---
    furina = Character("Furina")
    furina.hasElement, furina.hasWeapon = Hydro, Sword
    furina.hasRole = [SubDPS]
    furina.scalesWith = [HP]
    furina.recommendsSet = [GoldenTroupe, Tenacity]

    xingqiu = Character("Xingqiu")
    xingqiu.hasElement, xingqiu.hasWeapon = Hydro, Sword
    xingqiu.hasRole = [SubDPS]
    xingqiu.recommendsSet = [SeveredFate, Noblesse]

    zhongli = Character("Zhongli")
    zhongli.hasElement, zhongli.hasWeapon = Geo, Polearm
    zhongli.hasRole = [Support]
    # scaling Zhongli sengaja kosong: sumber tidak menyebut
    class Domain(Thing): pass
    class droppedIn(ObjectProperty):
        domain = [ArtifactSet]; range = [Domain]
    class recommendedDomain(ObjectProperty):
        domain = [Character]; range = [Domain]
    recommendedDomain.property_chain.append(PropertyChain([recommendsSet, droppedIn]))

    # TODO: ganti dengan nama domain asli dari wiki
    DomA, DomB = Domain("DOMAIN_TODO_A"), Domain("DOMAIN_TODO_B")
    GoldenTroupe.droppedIn = [DomA]
    Tenacity.droppedIn = [DomB]
    sync_reasoner(infer_property_values=True)   # HermiT

print("Furina is_a :", furina.is_a)
print("HPScaler    :", list(HPScaler.instances()))
print("Furina domain :", furina.recommendedDomain)
print("Xingqiu domain:", xingqiu.recommendedDomain)
out = os.path.join(os.path.dirname(__file__), "genshin.owl")
onto.save(file=out, format="rdfxml")
print("saved ->", out)
