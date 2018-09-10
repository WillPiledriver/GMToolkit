from helper import *

class Combat:
    def __init__(self):
        pass


class Weapons:
    def __init__(self, csv_file=None):
        self.csv = (csv_file, "data/weapons.csv")[csv_file is None]
        self.weapons = {}
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
        pass


class Armor:
    def __init__(self):
        pass
