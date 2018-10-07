import re


class Print:
    def __init__(self, edition, print_id, partiture):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture

    def format(self):
        return ""  # TODO

    def composition(self):
        return self.edition.composition

    def __repr__(self):
        return "Print ID: " + str(self.print_id) + \
               "\n\tPartiture: " + str(self.partiture) + \
               "\n\tEdition: \n" + str(self.edition)


class Edition:
    def __init__(self, composition, authors, name):
        self.composition = composition
        self.authors = authors
        self.name = name

    def __repr__(self):
        return "\t\tName: " + str(self.name) + \
               "\n\t\tAuthors: " + str(self.authors) + \
               "\n\t\tComposition: " + str(self.composition)

class Composition:
    def __init__(self, name, incipit, key, genre, year, voices, authors):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors

    def __str__(self):
        return "\n\t\t\tName: " + str(self.name) + \
               "\n\t\t\tincipit: " + str(self.incipit) + \
               "\n\t\t\tkey: " + str(self.key) + \
               "\n\t\t\tgenre: " + str(self.genre) + \
               "\n\t\t\tyear: " + str(self.year) + \
               "\n\t\t\tvoices: " + str(self.voices) + \
               "\n\t\t\tauthors: " + str(self.authors)


class Voice:
    def __init__(self, name, range):
        self.name = name
        self.range = range

    def __repr__(self):
        return "\tName: " + str(self.name) + \
               "\tRange: " + str(self.range)


class Person:
    def __init__(self, name, born, died):
        self.name = name
        self.born = born
        self.died = died

    def __repr__(self):
        return "\tName: " + self.name + \
               "\tBorn: " + str(self.born) + \
               "\tDied: " + str(self.died)


def load(filename):
    result = []
    file = open(filename, 'r', encoding='UTF8')
    content = file.read().split("\n\n")
    for part in content:  # One part in the content
        result.append(parse_print(part))
    # todo sort list
    return result


def parse_print(part):
    print_id = int(re.search(r"Print Number: ([0-9]+)", part).group(1))
    partiture = parse_partiture(part)
    edition = parse_edition(part)
    return Print(edition, print_id, partiture)


def parse_partiture(part):
    partiture = re.search(r"Partiture: (\w+)", part)
    if (partiture is None) or ("yes" not in partiture.group(1)):
        return False  # nothing or anything else except yes
    else:
        return True


def parse_edition(part):
    edition_name_search = re.search(r"Edition: ([\w\s]+)\n", part)
    if edition_name_search is None:
        edition_name = None
    else:
        edition_name = edition_name_search.group(1).strip()
    persons = parse_persons_from_editor(part)
    composition = parse_composition(part)
    return Edition(composition, persons, edition_name)


def parse_persons_from_editor(part):
    result = []
    persons_search = re.search(r"Editor: (.+)", part)
    if persons_search is None:
        return result
    names = persons_search.group(1)
    if "," not in names:  # only one name
        result.append(Person(names, None, None))
        return result
    else:
        return parse_name_by_comma(names)


# Parse name by comma. First comma is in the name and the second one is used for split the names.
# Function go through line by one character and save it to the buffer, when it found space or comma, they set flag.
# After that it knows that next comma split the name.
def parse_name_by_comma(names):
    result = []
    buffer = []
    was_space_or_surname_comma = False  # flag
    for c in names:
        if c != ',' and c != ' ':
            buffer.append(c)
        else:
            if c == ' ':
                if len(buffer) == 0:  # first space in the second (or next) name, it is not needed,
                    continue
                buffer.append(c)
                was_space_or_surname_comma = True
            else:
                if was_space_or_surname_comma:  # this is the separate comma, save buffer, reset buffer and flag
                    result.append(Person(''.join(buffer).strip(), None, None))
                    buffer.clear()
                    was_space_or_surname_comma = False
                else:  # just comma in the name, this comma has to be in the name
                    buffer.append(c)

    result.append(Person(''.join(buffer).strip(), None, None))  # buffer contains last name, append it
    buffer.clear()
    return result


def parse_composition(part):
    name_search = re.search(r"Title: (.+)", part)
    if name_search is None:
        name = None
    else:
        name = name_search.group(1).strip()
    incipit_search = re.search(r"Incipit: (.+)", part)
    if incipit_search is None:
        incipit = None
    else:
        incipit = incipit_search.group(1).strip()
    key_search = re.search(r"Key: (.+)", part)
    if key_search is None:
        key = None
    else:
        key = key_search.group(1).strip()
    genre_search = re.search(r"Genre: (.+)", part)
    if genre_search is None:
        genre = None
    else:
        genre = genre_search.group(1).strip()
    year_search = re.search(r"Composition Year: .*(\d{4}).*", part)
    if year_search is None:
        year = None
    else:
        year = int(year_search.group(1).strip())
    persons = parse_persons_from_composer(part)
    voices = parse_voices(part)
    return Composition(name, incipit, key, genre, year, voices, persons)


def parse_persons_from_composer(part):
    result = []
    persons_search = re.search(r"Composer: (.+)", part)
    if persons_search is None:
        return result
    persons = persons_search.group(1).split(';')
    for particular_person in persons:
        person_name = re.sub(r"[^A-Za-z\u00c0-\u017F ,]", '', particular_person).strip()
        born_regex = re.search(r"(\(\d{4}\-)", particular_person)  # (nnnn-
        if born_regex is None:
            born = None
        else:
            born = int(born_regex.group(1).lstrip("(").rstrip("-"))
        died_regex = re.search(r"(\d{4})(\))", particular_person)  # nnnn) or nnnn)
        if died_regex is None:
            died = None
        else:
            died = int(died_regex.group(1).rstrip(")"))
        result.append(Person(person_name, born, died))
    return result


def parse_voices(part):
    result = []
    voices_search = re.findall(r"Voice \d+:(.*)", part)
    for found_voice in voices_search:
        if found_voice.strip() == "":  # empty line or line which contains only white spaces
            result.append(Voice(None, None))
            continue
        if "--" not in found_voice: # range is not in the voice, so add all just a name
            result.append(Voice(found_voice.strip(), None))
        else:
            voice_regex = re.search(r"(\w+--\w+)[,;]?(.*)", found_voice)
            range = voice_regex.group(1).strip()
            name = voice_regex.group(2).strip()
            if name is '':
                result.append(Voice(None, range))
            else:
                result.append(Voice(name, range))
    return result
