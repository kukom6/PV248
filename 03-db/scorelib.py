import re


class Print:
    def __init__(self, edition, print_id, partiture):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture

    def format(self):
        #  print composer
        print("Print Number: {}".format(self.print_id))
        composition = self.edition.composition
        #  print composer
        print("Composer: ", end='')
        if not composition.authors:
            print("")  # empty [], no composer
        else:
            self.print_person_list(composition.authors, ";")  # in original file, separator between names is ;
        #  print title
        title = composition.name
        if title is None:
            print("Title: ")
        else:
            print("Title: {}".format(title))
        #  print genre
        genre = composition.genre
        if genre is None:
            print("Genre: ")
        else:
            print("Genre: {}".format(genre))
        #  print key
        key = composition.key
        if key is None:
            print("Key: ")
        else:
            print("Key: {}".format(key))
        #  print year
        year = composition.year
        if year is None:
            print("Composition Year: ")
        else:
            print("Composition Year: {}".format(year))
        #  print Edition
        edition = self.edition
        edition_name = edition.name
        if edition_name is None:
            print("Edition: ")
        else:
            print("Edition: {}".format(edition_name))
        #  print Editor
        print("Editor: ", end='')
        if not edition.authors:
            print("")  # empty [], no editors
        else:
            self.print_person_list(edition.authors, ",")  # in original file, separator between names is ,
        #  print Voices x
        voices = composition.voices
        if not voices:
            print("Voice 1: ")  # empty [], only Voice 1:
        else:
            i = len(voices)
            for x in range(0, i):
                voice_name = voices[x].name
                voice_range = voices[x].range
                if voice_name is None and voice_range is None:
                    print("Voice {}: ".format(x + 1))
                elif voice_name is None:
                    print("Voice {}: {}".format(x + 1, voice_range))
                elif voice_range is None:
                    print("Voice {}: {}".format(x + 1, voice_name))
                else:
                    print("Voice {}: {}; {}".format(x+1, voice_range, voice_name))
        #  print Partiture
        partiture = self.partiture
        if partiture:
            print("Partiture: yes")
        else:
            print("Partiture: no")
        #  print Incipit
        incipit = composition.incipit
        if incipit is None:
            print("Incipit: ")
        else:
            print("Incipit: {}".format(incipit))

    def composition(self):
        return self.edition.composition

    # auxiliary function because compositors and editors are the same formats.
    @staticmethod
    def print_person_list(persons, separator):
        i = len(persons)
        for x in range(0, i):
            person = persons[x]
            name = person.name
            born = person.born
            if born is None:
                born = ""
            died = person.died
            if died is None:
                died = ""
            if (person.born is None) and (person.died is None):
                print('{}'.format(name), end='')
            else:
                print('{} ({}--{})'.format(name, born, died), end='')
            if x < i - 1:
                print("{} ".format(separator), end='')
            else:
                print("")  # it was the last composer
                break


class Edition:
    def __init__(self, composition, authors, name):
        self.composition = composition
        self.authors = authors
        self.name = name


class Composition:
    def __init__(self, name, incipit, key, genre, year, voices, authors):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors


class Voice:
    def __init__(self, name, range):
        self.name = name
        self.range = range


class Person:
    def __init__(self, name, born, died):
        self.name = name
        self.born = born
        self.died = died


def load(filename):
    result = []
    file = open(filename, 'r', encoding='UTF8')
    content = file.read().split("\n\n")
    for part in content:  # One part in the content
        if part is "":  # When after last print is empty line, last content after split will be empty
            continue
        result.append(parse_print(part))
    result.sort(key=lambda x: x.print_id, reverse=False)
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
    edition_name_search = re.search(r"Edition: (.+)\n", part)
    if edition_name_search is None:
        edition_name = None
    else:
        edition_name = edition_name_search.group(1).strip()
        if edition_name == "":  # when in the value are spaces >1 , it is valid for regex but still it has to be None
            edition_name = None
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
        if "--" not in found_voice:  # range is not in the voice, so add all just a name
            result.append(Voice(found_voice.strip(), None))
        else:
            voice_regex = re.search(r"([\w\(\)]+--[\w\(\)]+)[,;]?(.*)", found_voice)  # some range contains ()
            range = voice_regex.group(1).strip()
            name = voice_regex.group(2).strip()
            if name is '':
                result.append(Voice(None, range))
            else:
                result.append(Voice(name, range))
    return result
