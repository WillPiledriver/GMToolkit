from helper import *
from pprint import pprint


class Characters:

    def __init__(self, client, game_name):
        self.game_name = game_name
        self.collection = client[game_name]["characters"]
        self._ids = [None, None, None, None]
        self.attributes = {}
        self.skills = {}
        self.secondary = {}
        self.bonus = {}
        self.load()
        self.t_list = []
        self.break_loop = False
        self.temp_calc = None

    def save(self):
        self.collection.update({"_id": self._ids[0]}, {"attributes": self.attributes}, True)
        self.collection.update({"_id": self._ids[1]}, {"skills":     self.skills},     True)
        self.collection.update({"_id": self._ids[2]}, {"secondary":  self.secondary},  True)
        self.collection.update({"_id": self._ids[3]}, {"bonus":      self.bonus},      True)

    def load(self):
        self.attributes = self.collection.find_one({"attributes": {"$exists": True}})
        self.skills = self.collection.find_one({"skills": {"$exists": True}})
        self.secondary = self.collection.find_one({"secondary": {"$exists": True}})
        self.bonus = self.collection.find_one({"bonus": {"$exists": True}})

        if self.attributes is None:
            print("Creating new attributes document")
            self.collection.insert_one({"attributes": {}})
            self.attributes = self.collection.find_one({"attributes": {"$exists": True}})
        if self.skills is None:
            print("Creating new skills document")
            self.collection.insert_one({"skills": {}})
            self.skills = self.collection.find_one({"skills": {"$exists": True}})
        if self.secondary is None:
            print("Creating new secondary document")
            self.collection.insert_one({"secondary": {}})
            self.secondary = self.collection.find_one({"secondary": {"$exists": True}})
        if self.bonus is None:
            print("Creating new bonus document")
            self.collection.insert_one({"bonus": {}})
            self.bonus = self.collection.find_one({"bonus": {"$exists": True}})

        self._ids = [self.attributes["_id"], self.skills["_id"], self.secondary["_id"], self.bonus["_id"]]
        self.attributes = self.attributes["attributes"]
        self.skills = self.skills["skills"]
        self.secondary = self.secondary["secondary"]
        self.bonus = self.bonus["bonus"]

    def edit_menu(self, choice=None):
        '''
        uses recursion to select which character global to edit
        '''
        if choice is None:
            self.break_loop = False
        while self.break_loop is False:
            if choice is None:
                self.edit_menu(choice=gen_menu(["Attributes", "Skills", "Secondary attributes", "Back"],
                                               "Edit character globals"))
            else:
                if choice == 3:
                    self.break_loop = True
                else:
                    if self.edit(choice):
                        choice = None

    def edit(self, category):
        '''
        Allows editing of attributes, skills, and secondary attributes.
        :param category: Which category to edit
        '''

        self.t_list = [self.attributes, self.skills, self.secondary]
        stuff = ["Attributes", "Skills", "Secondary Attributes"]
        if 0 > category > 3:  # This whole if statement is probably useless
            return False
        else:
            inp = gen_menu(list(self.t_list[category].keys()) + ["Add {}".format(stuff[category]), "Back"], "Edit {}".
                           format(stuff[category]))

            if inp == len(self.t_list[category]):
                # Add New
                var_name = input("VARIABLE NAME> ").upper()
                desc = input("DESCRIPTOR> ")
                self.t_list[category][var_name] = {"desc": desc, "val": None}

                # Skills and secondary
                if 0 < category < 3:
                    base_eq = input("Base Equation> ")

                    if base_eq is None:
                        base_eq = 0

                    self.t_list[category][var_name]["eq"] = base_eq

            elif 0 <= inp < len(self.t_list[category]):
                # Edit old
                pprint(self.t_list[category][list(self.t_list[category].keys())[inp]])
                var_name = input("VARIABLE NAME> ").upper()
                desc = input("DESCRIPTOR> ")
                del self.t_list[category][list(self.t_list[category].keys())[inp]]
                self.t_list[category][var_name] = {"desc": desc, "val": None}

                # Skills and secondary
                if 0 < category < 3:
                    base_eq = input("Base Equation> ")

                    if base_eq is None:
                        base_eq = 0

                    self.t_list[category][var_name]["eq"] = base_eq
            else:
                return True

            self.attributes = self.t_list[0]
            self.skills = self.t_list[1]
            self.secondary = self.t_list[2]
            self.save()
            return False

    def calc_base(self, attributes, eq):
        '''
        Calculates a given equation by replacing strings with variables.
        :param attributes: Dict of attributes with "var" keys.
        :param eq: Equation to perform.
        :return: Solution of the equation.
        '''

        attributes = {key: attributes[key]["val"] for key in attributes.keys()}
        for key in attributes:
            eq = eq.replace("{"+key+"}", str(attributes[key]))
        exec("self.temp_calc=" + eq)
        return self.temp_calc


class Party:

    def __init__(self, client, game_name, characters_handle):
        self.ch = characters_handle
        self.game_name = game_name
        self.collection = client[self.game_name]["party"]
        self.party = {}
        self.break_loop = False
        self.load()

    def save(self):
        for name in self.party:
            self.collection.update({name: {"$exists": True}}, {name: self.party[name]}, True)

    def load(self):

        total = self.collection.find()
        load_this = {}
        for i in range(total.count()):
            del total[i]["_id"]
            load_this.update(total[i])
        del load_this["_id"]
        self.party = load_this

    def party_menu(self, choice=None):
        menu = [key for key in list(self.party.keys())]
        while choice != len(menu) + 1:
            if choice is None:
                choice = gen_menu(menu + ["Add new party member", "Back"], "Edit Party Menu")
                continue
            else:
                if choice == len(menu):
                    name = self.edit_member(None)
                    menu = [key for key in list(self.party.keys())]
                    choice = menu.index(name)
                    continue
                if self.edit_member(menu[choice]):
                    choice = None

    def edit_member(self, c):
        if c is None:
            print("Add new")
            new_name = input("Character nickname> ")
            self.party[new_name] = {}
            self.party[new_name]["attributes"] = {key: dict(self.ch.attributes[key]) for key in self.ch.attributes}
            return new_name
        elif c in self.party:
            print("Edit")
            for attribute in self.party[c]["attributes"]:
                self.party[c]["attributes"][attribute]["val"] = int(input(
                    "Enter value for {} ({})> ".format(self.party[c]["attributes"][attribute]["desc"], attribute)))

            self.populate(c, self.party[c]["attributes"])

            inp = (None, "Y")[input("Would you like to enter bonuses? ").upper() == "Y"]
            while inp:
                inp = input("VAR_NAME> ").upper()
                if len(inp) == 0:
                    break
                value = int(input("VAL> "))
                self.party[c]["bonus"][inp] = value
            self.save()
            return True
        else:
            print("what?")
            return False

    def populate(self, name, attributes):
        self.party[name]["skills"] = {key: dict(self.ch.skills[key]) for key in self.ch.skills}
        self.party[name]["secondary"] = {key: dict(self.ch.secondary[key]) for key in self.ch.secondary}
        self.party[name]["bonus"] = {}

        for skill in self.ch.skills.keys():
            self.party[name]["skills"][skill]["val"] = self.ch.calc_base(attributes, self.ch.skills[skill]["eq"])
            print("{}: {}%".format(self.ch.skills[skill]["desc"], self.ch.calc_base(attributes,
                                                                                    self.ch.skills[skill]["eq"])))

        for secondary in self.ch.secondary.keys():
            self.party[name]["secondary"][secondary]["val"] = self.ch.calc_base(attributes,
                                                                                self.ch.secondary[secondary]["eq"])
            print("{}: {}".format(self.ch.secondary[secondary]["desc"],
                                  self.ch.calc_base(attributes, self.ch.secondary[secondary]["eq"])))

class NPC:

    def __init__(self, enemies_file=None):
        self.enemies = {}
        if enemies_file is None:
            self.enemies_file = "data/enemies.csv"
        else:
            self.enemies_file = enemies_file
        self.load()
        pass


    def load(self):
        with(open(self.enemies_file)) as csvfile:
            enemies = csv.DictReader(csvfile)
            for row in enemies:

                for key in row.keys():
                    print("{}: {}".format(key, row[key]))
                    if key == "NAME":
                        continue
