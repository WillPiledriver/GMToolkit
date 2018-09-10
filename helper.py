from os import system
from pymongo import MongoClient
from pprint import pprint
import math
import csv
import re
import random as rand


def clear(): system("cls")


def pause(): system("pause")


def gen_menu(options, comment=None, cls=True):
    c = 0
    if cls:
        clear()
    else:
        print("")

    if len(options) == 0:
        print("There were no options passed to the gen_menu function")
        return None
    elif len(options) == 1:
        print("Forced option [{}] because it was the only one.".format(options[0]))
        return 0

    if comment:
        print(comment)

    for o_num in range(len(options)):
        print("{}> {}".format(str(o_num + 1), options[o_num]))

    option = None
    while option is None:
        try:
            option = int(input(">> "))
            if option < 1 or option > (len(options)):
                c += 1
                option = None
                if c == 3:
                    option = 0
                    break
                print("Choose one of the options above. [{}/3]".format(c))

        except Exception as e:
            print("Please input a number.")
    return option - 1


def roll(s, mod=0):
    if re.match(re.compile("^[0-9]+d[0-9]+$"), s.lower()):
        p = s.lower().split("d")
        rolls = [rand.randint(1, int(p[1])) for i in range(int(p[0]))]
    elif re.match(re.compile("^[0-9]+$"), s):
        rolls = [int[s]]
    else:
        print("You fucked up")
        rolls = [0]
        pause()
    return rolls, sum(rolls) + mod
