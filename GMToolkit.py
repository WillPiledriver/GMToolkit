from helper import *
from Characters import Characters, Party
from random import randint


def test():
    sp = {}
    for s in "SPECIAL":
        sp[s] = {"val": randint(1,10)}

    pprint(sp)

    for skill in c.skills.keys():
        print("{}: {}%".format(c.skills[skill]["desc"], c.calc_base(sp, c.skills[skill]["eq"])))

    for secondary in c.secondary.keys():
        print("{}: {}".format(c.secondary[secondary]["desc"], c.calc_base(sp, c.secondary[secondary]["eq"])))

    pause()


def main_menu():
    do = [c.edit_menu, p.party_menu, test, clear]

    option = gen_menu(["Edit character globals", "Edit party", "Test", "Clear screen"], comment="Main Menu")
    do[option]()


client = MongoClient()
db_name = input("Enter name of game> ")
c = Characters(client, db_name)
p = Party(client, db_name)
while True:
    main_menu()
