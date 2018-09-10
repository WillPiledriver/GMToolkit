from helper import *
from Characters import Characters, Party, NPC
from Combat import Combat, Weapons, Armors





def main_menu():
    do = [c.edit_menu, p.party_menu, clear]

    option = gen_menu(["Edit character globals", "Edit party", "Clear screen"], comment="Main Menu")
    do[option]()


client = MongoClient()
db_name = "fallout" #input("Enter name of game> ")
c = Characters(client, db_name)
p = Party(client, db_name, characters_handle=c)
w = Weapons(csv_file="data/weapons.csv")
a = Armors(csv_file="data/armors.csv")
npc = NPC(weapons_handle=w, characters_handle=c)
npc.generate_enemy("Scumbag")

while True:
    main_menu()
