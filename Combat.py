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
        self.temp = None

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
        """
        First: Reorganize data by removing unnecessary keys, and combining skills, attributes, and secondary statistics
        Second: Generate weapons and armor.
        Third: Calculate bonuses
        :param session_name:
        :return:
        """
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
            _session[combatant_name]["bonus"] = session[combatant_name]["bonus"]
            if self.is_party(combatant_name) is False:
                _session[combatant_name]["XP"] = int(self.npc.enemies[_session[combatant_name]["NAME"]]["XP"])
            else:
                _session[combatant_name]["XP"] = 0

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

        # Generate Bonuses
        for combatant_name in list(_session.keys()):
            if len(_session[combatant_name]["bonus"]) > 0:
                for k, v in _session[combatant_name]["bonus"].items():
                    _session[combatant_name][k] += v
                _session[combatant_name]["bonus"] = {}
            _session[combatant_name]["AC"] += _session[combatant_name]["armor"]["AC"]
            if len(_session[combatant_name]["armor"]["BONUS"]) > 0:
                for k, v in _session[combatant_name]["armor"]["BONUS"].items():
                    _session[combatant_name][k] += v

        party_members = [name for name in list(_session.keys()) if self.is_party(name)]
        enemy_members = [name for name in list(_session.keys()) if self.is_party(name) is False]
        # Turn Order
        rounds = 0
        total_xp = 0
        while len(party_members) > 0 and len(enemy_members) > 0:
            rounds += 1
            turn = 0
            for (name, seq) in turn_order:
                ap_used = 0
                ap = _session[name]["AP"]
                turn += 1
                print("\n" + "*"*79)
                in_party = self.is_party(name)
                weapon = _session[name]["weapon"]
                attack = ["Attack Target", "Attack Random"]
                members = (party_members, enemy_members)[in_party]
                while ap_used <= ap:
                    if ap_used + weapon["AP"] > ap:
                        attack = []
                    menu = attack + ["Set HP", "Pass"]
                    choice = gen_menu(menu, "{}'s turn\t\tAP: {}\t\tHP: {}".format(name, ap - ap_used,
                                                                                   _session[name]["HP"]), False)
                    if (choice == 0) and (len(attack) > 0):
                        # Attack Target
                        defender = members[gen_menu(["{}\n\tWeapon: {}\t\tArmor: {}\t\tHP: {}"
                                                 .format(enemy, _session[enemy]["weapon"]["NAME"],
                                                         _session[enemy]["armor"]["NAME"],
                                                         _session[enemy]["HP"])
                                                 for enemy in members], "Choose target", False)]
                        ap_used += weapon["AP"]

                    elif (choice == len(attack) - 1) and (len(attack) > 0):
                        # Attack Random
                        defender = rand.choice(members)
                        ap_used += weapon["AP"]

                    elif choice == len(menu) - 2:
                        # Set HP
                        _session[name]["HP"] = int(input("New HP> "))
                        continue
                    elif choice == len(menu) - 1:
                        break
                    defender_ac = _session[defender]["AC"]
                    print("AC {}    {}: {}".format(defender_ac, weapon["TYPE"], _session[name][weapon["TYPE"]]))
                    ammo_damage = 0
                    ammo = None
                    if weapon["TYPE"] == "SG":
                        ammo = self.wh.ammo[weapon["AMMO"]]
                        ammo_damage = roll(ammo["DMG"])[1]
                        defender_ac += ammo["AC"]
                    else:
                        pass
                    print("_"*79)
                    print("{} is attacking {} with a {}".format(name, defender, weapon["NAME"]))
                    if in_party:
                        r = input("roll to hit> ")
                        if r == '':
                            roll_to_hit = roll("1d100")[1]
                        else:
                            roll_to_hit = int(r)
                    else:
                        roll_to_hit = roll("1d100")[1]

                    need = _session[name][weapon["TYPE"]] - defender_ac
                    print("Roll to hit: {}\n\tNeed: {}".format(roll_to_hit, need))

                    if roll_to_hit <= _session[name]["CRIT"]:
                        print("Critical hit")
                    elif roll_to_hit > 97:
                        print("Critical Failure")
                        continue
                    elif roll_to_hit <= need:
                        pass
                    else:
                        print("Attack missed")
                        continue
                    exec("self.temp = " + weapon["DB"].replace("{MD}", str(_session[name]["MD"])))

                    if in_party:
                        r = input("roll for damage> ")
                        if r == '':
                            roll_for_damage = roll(weapon["DMG"])[1]
                        else:
                            roll_for_damage = int(r)
                    else:
                        roll_for_damage = roll(weapon["DMG"])[1]

                    damage_bonus = self.temp

                    if ammo_damage > 0:
                        if in_party:
                            r = input("roll for bullet damage> ")
                            if r == '':
                                ammo_damage = roll(ammo["DMG"])[1]
                            else:
                                ammo_damage = int(r)
                        damage_bonus += ammo_damage
                    init_dmg = damage_bonus + roll_for_damage
                    print("{}dmg + {} bonus = {} TOTAL".format(roll_for_damage, damage_bonus, init_dmg))

                    # Final damage

                    dt = _session[defender]["armor"]["N"][0]
                    dr = _session[defender]["armor"]["N"][1]

                    if weapon["TYPE"] == "SG":
                        dt = dt * ammo["DT"]
                        dr += ammo["DR"]
                    real_damage = (init_dmg - dt) - math.floor((init_dmg - dt) * (dr / 100))
                    print("After damage reduction: {}".format(real_damage))
                    _session[defender]["HP"] -= real_damage

                    if _session[defender]["HP"] < 1:
                        total_xp += _session[defender]["XP"]
                        print("{} HAS BEEN SLAIN GRANTING {} XP".format(defender, _session[defender]["XP"]))
                        if self.is_party(defender):
                            party_members.remove(defender)
                        else:
                            enemy_members.remove(defender)
                        del _session[defender]
                        break

        print("Combat complete.\n\tXP earned: {}".format(total_xp))


class Weapons:
    def __init__(self, csv_file=None):
        self.csv = (csv_file, "data/weapons.csv")[csv_file is None]
        self.weapons = dict()
        self.ammo = dict()
        self.load()
        self.load_ammo()

    def load(self):
        with(open(self.csv)) as csvfile:
            ef = csv.DictReader(csvfile)
            for row in ef:
                self.weapons[row["NAME"]] = {}
                for key in row.keys():
                    if key == "NAME":
                        continue
                    self.weapons[row["NAME"]][key] = row[key]

    def load_ammo(self):
        ints = ["AC", "DR", "DT"]
        with(open("data/ammo.csv")) as csvfile:
            ef = csv.DictReader(csvfile)
            for row in ef:
                self.ammo[row["NAME"]] = {}
                for key in row.keys():
                    if key == "NAME":
                        continue
                    elif key in ints:
                        self.ammo[row["NAME"]][key] = int(row[key])
                        continue
                    self.ammo[row["NAME"]][key] = row[key]

    def generate_weapon(self, weapon):
        ints = ["AP", "RANGE"]
        for k, v in self.weapons[weapon].items():
            if k in ints:
                self.weapons[weapon][k] = int(v)

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
