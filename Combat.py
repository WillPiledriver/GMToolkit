from helper import *

class Combat:
    def __init__(self, client, db_name, npc_handle, weapons_handle, armors_handle, characters_handle, party_handle):
        self.npc = npc_handle
        self.wh = weapons_handle
        self.ah = armors_handle
        self.ch = characters_handle
        self.ph = party_handle
        self.party_members = list(self.ph.party.keys())
        self.collection = client[db_name]["combat"]
        self.break_loop = False
        self.sessions = dict()
        self.load()

    def load(self):
        total = self.collection.find()
        load_this = {}
        for i in range(total.count()):
            del total[i]["_id"]
            load_this.update(total[i])
        if "_id" in load_this:
            del load_this["_id"]
        self.sessions = load_this

    def save(self):
        for name in self.sessions:
            self.collection.update({name: {"$exists": True}}, {name: self.sessions[name]}, True)

    def combat_menu(self, choice=None):
        if choice is None:
            self.break_loop = False
        while self.break_loop is False:
            if choice is None:
                self.combat_menu(choice=gen_menu(["Start new combat session", "Open session", "Back"],
                                               "Combat Menu"))
            else:
                if choice == 2:
                    self.break_loop = True
                else:
                    if self.combat_switch(choice):
                        choice = None

    def combat_switch(self, choice):
        if choice == 0:
            name = input("Session name> ")
            self.session_menu(name)
            self.save()
            return True
        elif choice == 1:
            name = input("Session name> ")
            self.session_menu(name, edit=True)
            self.save()
            return True

        return True

    def session_menu(self, session_name, edit=False):
        if edit is False:
            self.sessions[session_name] = dict()

        inp = gen_menu(["New Enemy", "Add Party Member", "Reroll", "Skirmish", "Back"],
                       "Combat session ({})".format(session_name))
        while inp != 4:
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
                self.save()
                print("{}\t\tWeapon: {}\t\tArmor: {}".format(enemy_name, enemy["weapon"], enemy["armor"]))
                print("\t\t".join(["Attributes:\n"] +
                                ["{} {}".format(key, self.sessions[session_name][enemy_name]["attributes"][key]["val"])
                                 for key in self.sessions[session_name][enemy_name]["attributes"]]))
                print("\t".join(["Skills:\n"] +
                                ["{} {}".format(key, self.sessions[session_name][enemy_name]["skills"][key]["val"])
                                 for key in self.sessions[session_name][enemy_name]["skills"]]))
                print("\t".join(["Secondary:\n"] +
                                ["{} {}".format(key, self.sessions[session_name][enemy_name]["secondary"][key]["val"])
                                 for key in self.sessions[session_name][enemy_name]["secondary"]]))
            elif inp == 1:
                # Add Party Member
                member = gen_menu(self.party_members + ["Back"], comment="Add Party Member", cls=False)
                if member == len(self.party_members):
                    pass
                else:
                    member_name = self.party_members[member]
                    self.sessions[session_name][member_name] = self.ph.party[member_name]
                    self.save()
            elif inp == 2:
                # Reroll
                for enemy_name in self.sessions[session_name].keys():
                    if enemy_name in self.ph.party:
                        print(enemy_name)
                        continue
                    original_name = self.sessions[session_name][enemy_name]["attributes"]["NAME"]["val"]
                    enemy = self.npc.generate_enemy(original_name)
                    self.sessions[session_name][enemy_name] = enemy
                    print("{}\t\tWeapon: {}\t\tArmor: {}".format(enemy_name, enemy["weapon"], enemy["armor"]))
                    print("\t\t".join(["Attributes:\n"] +
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
            elif inp == 3:
                # Skirmish
                self.skirmish(session_name)
            inp = gen_menu(["New Enemy", "Add Party Member", "Reroll", "Skirmish", "Back"],
                           "Combat session ({})".format(session_name), False)

    def is_party(self, name):
        return name in self.party_members

    def skirmish(self, session_name):
        '''
        First: Reorganize data by removing unnecessary keys, and combining skills, attributes, and secondary statistics
        Second: Generate weapons and armor.
        Third: Calculate bonuses
        :param session_name:
        :return:
        '''
        session = dict(self.sessions[session_name])
        _session = dict()
        combine_these = ["skills", "attributes", "secondary"]
        for combatant_name in list(session.keys()):
            _session[combatant_name] = dict()
            for c in combine_these:
                _session[combatant_name].update(session[combatant_name][c])

        for combatant_name in list(_session.keys()):
            for var in list(_session[combatant_name].keys()):
                _session[combatant_name][var] = _session[combatant_name][var]["val"]
        
        # Calculate turn order based on SE (sequence)
        turn_order = list()
        for combatant_name in list(_session.keys()):
            turn_order.append((combatant_name, _session[combatant_name]["SE"]))
        turn_order = sorted(turn_order, key=itemgetter(1), reverse=True)

        # Generate armor
        for combatant_name in list(_session.keys()):
            _session[combatant_name]["armor"] = dict()
            if "armor" in session[combatant_name]:
                a = session[combatant_name]["armor"]
            else:
                a = "nothing"
            arm = self.ah.generate_armor(a)
            arm["NAME"] = a
            _session[combatant_name]["armor"] = arm

        # Generate weapon
        for combatant_name in list(_session.keys()):
            _session[combatant_name]["weapon"] = dict()
            if "weapon" in session[combatant_name]:
                w = session[combatant_name]["weapon"]
            else:
                w = "fist"
            wep = self.wh.generate_weapon(w)
            wep["NAME"] = w
            _session[combatant_name]["weapon"] = wep

        pass
        
        


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

    def generate_weapon(self, weapon):
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

    def generate_armor(self, armor):
        randnum_match = re.compile("^[0-9]+-[0-9]+$")
        num_match = re.compile("^[0-9]+$")
        result = dict(self.armors[armor])
        for key, value in result.items():
            if isinstance(value, (str,)) is False:
                continue
            if re.match(num_match, value):
                # Any integer
                result[key] = int(value)
            elif re.match(randnum_match, value):
                # Random number range
                splt = value.split("-")
                r = rand.randint(int(splt[0]), int(splt[1]))
                result[key] = r
            if value.count(",") > 0:
                # random list of strings
                result[key] = value.split(",")
        
        if len(result["BONUS"]) > 0:
            # Parse and restructure bonuses
            if isinstance(result["BONUS"], (list,)):
                bns = {}
                for b in result["BONUS"]:
                    splt = b.split(" ")
                    if re.match(randnum_match, splt[1]):
                        splt2 = splt[1].split("-")
                        bns[splt[0]] = rand.randint(int(splt2[0]), int(splt2[1]))
                    else:
                        bns[splt[0]] = int(splt[1])
                result["BONUS"] = bns
            else:
                splt = result["BONUS"].split(" ")
                if re.match(randnum_match, splt[1]):
                    splt2 = splt[1].split("-")
                    r = rand.randint(int(splt2[0]), int(splt2[1]))
                else:
                    r = int(splt[1])
                result["BONUS"] = {splt[0]: r}
        return result