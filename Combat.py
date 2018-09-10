from helper import *

class Combat:
    def __init__(self):
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
