from helper import *
from Characters import Characters, Party, NPC
from Combat import Combat, Weapons, Armors


def main_menu():
    do = [c.edit_menu, p.party_menu, combat.combat_menu, clear]

    option = gen_menu(["Edit character globals", "Edit party", "Combat Menu", "Clear screen"], comment="Main Menu")
    do[option]()


client = MongoClient()
db_name = "fallout" #input("Enter name of game> ")
c = Characters(client, db_name)
p = Party(client, db_name, characters_handle=c)
w = Weapons(csv_file="data/weapons.csv")
a = Armors(csv_file="data/armors.csv")
npc = NPC(weapons_handle=w, characters_handle=c)
combat = Combat(client, db_name, npc, w, a, c)

while True:
    main_menu()
