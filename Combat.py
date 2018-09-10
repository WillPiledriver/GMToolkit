from helper import *

class Combat:
    def __init__(self, client, db_name, npc_handle, weapons_handle, armors_handle, characters_handle):
        self.npc = npc_handle
        self.wh = weapons_handle
        self.ah = armors_handle
        self.ch = characters_handle
        self.collection = client[db_name]["combat"]
        self.break_loop = False
        self.sessions = dict()

    def combat_menu(self, choice=None):
        if choice is None:
            self.break_loop = False
        while self.break_loop is False:
            if choice is None:
                self.combat_menu(choice=gen_menu(["Start new combat session", "Back"],
                                               "Combat Menu"))
            else:
                if choice == 1:
                    self.break_loop = True
                else:
                    if self.combat_switch(choice):
                        choice = None

    def combat_switch(self, choice):
        if choice == 0:
            name = input("Session name> ")
            self.new_combat(name)

            return True
        return True

    def new_combat(self, session_name):
        self.sessions[session_name] = dict()

        inp = gen_menu(["New Enemy", "Reroll", "Skirmish", "Back"], "New combat session ({})".format(session_name))
        while inp != 3:
            if inp == 0:
                # New Enemy
                enemy_name = input("Enemy Name> ")
                original_name = enemy_name
                enemy = self.npc.generate_enemy(enemy_name)
                c = 2
                while enemy_name in self.sessions[session_name]:
                    enemy_name = "{} {}".format(original_name, c)
                    c += 1
                self.sessions[session_name][enemy_name] = enemy
                print(enemy_name)
                print("\t".join(["Attributes:\n"] +
                                ["{} {}".format(key, self.sessions[session_name][enemy_name]["attributes"][key]["val"])
                                 for key in self.sessions[session_name][enemy_name]["attributes"]]))
                print("\t".join(["Skills:\n"] +
                                ["{} {}".format(key, self.sessions[session_name][enemy_name]["skills"][key]["val"])
                                 for key in self.sessions[session_name][enemy_name]["skills"]]))
                print("\t".join(["Secondary:\n"] +
                                ["{} {}".format(key, self.sessions[session_name][enemy_name]["secondary"][key]["val"])
                                 for key in self.sessions[session_name][enemy_name]["secondary"]]))
            elif inp == 1:
                # Reroll
                for enemy_name in self.sessions[session_name].keys():
                    if enemy_name in self.ch.party:
                        continue
                    original_name = self.sessions[session_name][enemy_name]["attributes"]["NAME"]["val"]
                    enemy = self.npc.generate_enemy(original_name)
                    self.sessions[session_name][enemy_name] = enemy
                    print(enemy_name)
                    print("\t".join(["Attributes:\n"] +
                                    ["{} {}".format(key,
                                                    self.sessions[session_name][enemy_name]["attributes"][key]["val"])
                                     for key in self.sessions[session_name][enemy_name]["attributes"]]))
                    print("\t".join(["Skills:\n"] +
                                    ["{} {}".format(key, self.sessions[session_name][enemy_name]["skills"][key]["val"])
                                     for key in self.sessions[session_name][enemy_name]["skills"]]))
                    print("\t".join(["Secondary:\n"] +
                                    ["{} {}".format(key,
                                                    self.sessions[session_name][enemy_name]["secondary"][key]["val"])
                                     for key in self.sessions[session_name][enemy_name]["secondary"]]))

            inp = gen_menu(["New Enemy", "Reroll", "Skirmish", "Back"], "New combat session ({})".format(session_name),
                           False)


class Weapons:
    def __init__(self, csv_file=None):
        self.csv = (csv_file, "data/weapons.csv")[csv_file is None]
        self.weapons = dict()
        self.load()

    def load(self):
        with(open(self.csv)) as csvfile:
            ef = csv.DictReader(csvfile)
            for row in ef:
                self.weapons[row["NAME"]] = {}
                for key in row.keys():
                    if key == "NAME":
                        continue
                    self.weapons[row["NAME"]][key] = row[key]

    def get(self, weapon):
        return self.weapons[weapon]


class Armors:
    def __init__(self, csv_file=None):
        self.csv = (csv_file, "data/armors.csv")[csv_file is None]
        self.armors = dict()
        self.load()

    def load(self):
        with(open(self.csv)) as csvfile:
            ef = csv.DictReader(csvfile)
            for row in ef:
                self.armors[row["NAME"]] = {}
                for key in row.keys():
                    if key == "NAME":
                        continue
                    elif key in "NLFPE":
                        splt = row[key].split("/")
                        self.armors[row["NAME"]][key] = (int(splt[0]), int(splt[1]))
                        continue
                    self.armors[row["NAME"]][key] = row[key]

    def get(self, armor):
        return self.armors[armor]
