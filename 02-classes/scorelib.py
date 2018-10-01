class Print:
    def __init__(self, edition, print_id, partiture):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture

    def format(self):
        return ""

    def composition(self):
        return self.edition.composition


class Edition:
    def __init__(self, composition, authors, name=None):
        self.composition = composition
        self.authors = authors
        self.name = name


class Composition:
    def __init__(self, name=None, incipit=None, key=None, genre=None, year=None, voices=[], authors=[]):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors


class Voice:
    def __init__(self, name=None, range=None):
        self.name = name
        self.range = range


class Person:
    def __init__(self, name, born=None, died=None):
        self.name = name
        self.born = born
        self.died = died


def load(filename):
    result = Print()
    # todo sort list
    return result

