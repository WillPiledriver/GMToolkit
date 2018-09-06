from helper import *
from Characters import Characters, Party
from random import randint





def main_menu():
    do = [c.edit_menu, p.party_menu, clear]

    option = gen_menu(["Edit character globals", "Edit party", "Clear screen"], comment="Main Menu")
    do[option]()


client = MongoClient()
db_name = input("Enter name of game> ")
c = Characters(client, db_name)
p = Party(client, db_name, c)
while True:
    main_menu()
