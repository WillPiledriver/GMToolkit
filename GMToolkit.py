from helper import *
from Characters import Characters, Party, NPC
from Combat import Combat, Weapons, Armor





def main_menu():
    do = [c.edit_menu, p.party_menu, clear]

    option = gen_menu(["Edit character globals", "Edit party", "Clear screen"], comment="Main Menu")
    do[option]()


client = MongoClient()
db_name = "fallout" #input("Enter name of game> ")
c = Characters(client, db_name)
p = Party(client, db_name, c)
w = Weapons(csv_file="data/weapons.csv")
npc = NPC(weapons_handle=w)

while True:
    main_menu()
