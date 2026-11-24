from owlready2 import *

onto = get_ontology("http://test.org/t.owl")
with onto:
    class Character(Thing): pass
    class Hydro(Character): pass
    f = Hydro("furina")

sync_reasoner()          # HermiT bawaan
print("OK:", list(onto.individuals()))
