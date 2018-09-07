from os import system
from pymongo import MongoClient
from pprint import pprint
import math
import csv


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
