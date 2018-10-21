import sys
import scorelib
import sqlite3

sql_schema = open("./scorelib.sql", 'r', encoding='UTF8').read()

def main():
    if len(sys.argv) != 3:
        print("Numbers of parameter are wrong")
    else:
        to_db(scorelib.load(sys.argv[1]))


def to_db(prints):
    connection = sqlite3.connect(sys.argv[2])
    cursor = connection.cursor()

    table_exist = cursor.execute("SELECT name "
                                 "FROM sqlite_master "
                                 "WHERE type='table' "
                                 "AND name IN ('person','score','voice','edition','score_author',"
                                 "'edition_author','print');").fetchall()
    if table_exist:
        cursor.execute("DROP TABLE person")
        cursor.execute("DROP TABLE score")
        cursor.execute("DROP TABLE voice")
        cursor.execute("DROP TABLE edition")
        cursor.execute("DROP TABLE score_author")
        cursor.execute("DROP TABLE edition_author")
        cursor.execute("DROP TABLE print")

    cursor.executescript(sql_schema)

    for one_print in prints:
        save_print(one_print, cursor)
    cursor.close()
    connection.commit()


def save_print(print, cursor):
    id_edition = save_edition(print.edition, cursor)
    cursor.execute("INSERT INTO print (id, partiture, edition) VALUES (?, ?, ?)",
                   (print.print_id, 'Y' if print.partiture else 'N', id_edition))


# save edition method, two editions are same ONLY if edition and editor are same
def save_edition(edition, cursor):
    id_compostion = save_composition(edition.composition, cursor)
    exist_editions = cursor.execute("SELECT * FROM edition WHERE name IS ?", (edition.name,)).fetchall()

    # found editions with the same name, need to check editors whether are same
    if exist_editions:
        exactly_same = False
        for exist_composition in exist_editions:
            edition_id = exist_composition[0]
            editors_for_this_editor = cursor.execute("SELECT person.name FROM edition_author JOIN person "
                                                                 "WHERE edition_author.edition = ? AND "
                                                                 "edition_author.editor=person.id",
                                                                 (edition_id,)).fetchall()
            #  need to check whether the composition are same, in case function save_composition return key which is not
            #  in the db, the editor cannot be same, but when function returns id which is in DB need to check whether
            # id belongs to the specific composition
            if same_persons(edition.authors, editors_for_this_editor) and composition_are_same(id_compostion, edition_id, cursor):
                edition_id = exist_composition[0]
                exactly_same = True
                break
        # for didn't find any same edition with editors in DB, edition can be added to DB
        if not exactly_same:
            cursor.execute("INSERT INTO edition (score, name, year) VALUES (?, ?, ?)",
                           (id_compostion, edition.name, None))
            edition_id = cursor.lastrowid
    # in db is not similar edition, just add this one
    else:
        cursor.execute("INSERT INTO edition (score, name, year) VALUES (?, ?, ?)",
                       (id_compostion, edition.name, None))
        edition_id = cursor.lastrowid

    # Save persons and create connection M:N
    ids_authors = save_persons(edition.authors, cursor)
    for id_author in ids_authors:
        exist_connection = cursor.execute("SELECT * FROM edition_author WHERE edition = ? AND editor = ?",
                                          (edition_id, id_author)).fetchall()
        if not exist_connection:
            cursor.execute("INSERT INTO edition_author (edition, editor) VALUES (?, ?)", (edition_id, id_author))

    return edition_id


def composition_are_same(id_composition,  edition_id, cursor):
    editors_for_this_editor = cursor.execute("SELECT * FROM edition JOIN score "
                                             "WHERE edition.score = score.id "
                                             "AND edition.id = ? "
                                             "AND score.id = ?",
                                             (edition_id, id_composition)).fetchone()
    return editors_for_this_editor


# save composition method, method check whether the composition is not in the DB, but not only in score table but
# also in person and voice table, because two compositions are same ONLY when authors(persons) and voices are same too
def save_composition(composition, cursor):
    exist_compositions = cursor.execute("SELECT * FROM score WHERE "
                                        "name IS ? AND genre IS ? AND key IS ? AND incipit IS ? AND year IS ?",
                                        (composition.name, composition.genre, composition.key, composition.incipit,
                                         composition.year)).fetchall()
    # found compositions in DB on basic parameters, they have to be checked with composers and voices
    if exist_compositions:
        exactly_same = False
        # can be more same composition in DB, if found at least one exactly same, breaks search
        for exist_composition in exist_compositions:
            composition_id = exist_composition[0]
            composers_name_for_this_composition = cursor.execute("SELECT person.name FROM score_author JOIN person "
                                                                 "WHERE score_author.score = ? AND "
                                                                 "score_author.composer=person.id",
                                                                 (composition_id,)).fetchall()
            voices_for_this_composition = cursor.execute(
                "SELECT voice.name, voice.range FROM voice WHERE voice.score = ?", (composition_id,)).fetchall()
            if same_persons(composition.authors, composers_name_for_this_composition) \
                    and same_voices(composition.voices, voices_for_this_composition):
                # !FOUND IT! this composition in DB is exactly same
                composition_id = exist_composition[0]
                exactly_same = True
                break
        #  for didn't find any same composition in DB, composition can be added to DB
        if not exactly_same:
            cursor.execute("INSERT INTO score (name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)",
                          (composition.name, composition.genre, composition.key, composition.incipit, composition.year))
            composition_id = cursor.lastrowid
    # in db is not similar composition, just add this one
    else:
        cursor.execute("INSERT INTO score (name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)",
                       (composition.name, composition.genre, composition.key, composition.incipit, composition.year))
        composition_id = cursor.lastrowid

    save_voices(composition.voices, cursor, composition_id)

    # connect M:N
    ids_authors = save_persons(composition.authors, cursor)
    for id_author in ids_authors:
        exist_connection = cursor.execute("SELECT * FROM score_author WHERE score = ? AND composer = ?",
                                          (composition_id, id_author)).fetchall()
        if not exist_connection:
            cursor.execute("INSERT INTO score_author (score, composer) VALUES (?, ?)", (composition_id, id_author))
    return composition_id


# Test whether person list from code and name list of tuples from DB are same
def same_persons(person_list, names_from_db_raw):
    name_list = []
    for touple in names_from_db_raw:
        name_list.append(touple[0])

    if len(person_list) != len(name_list):
        return False
    for person in person_list:
        if person.name not in name_list:
            return False
    return True


# Test whether voices list from code and voices list from DB are same
def same_voices(voices_list, voices_from_db_tuples):
    db_voices_list = convert_voices(voices_from_db_tuples)

    if len(voices_list) != len(db_voices_list):
        return False
    for voice in voices_list:
        if voice not in db_voices_list:  # works due to __eq__ on voice
            return False
    return True


def convert_voices(voices_from_db_tuples):
    voices_from_db_list = []
    for voice_db in voices_from_db_tuples:
        voices_from_db_list.append(scorelib.Voice(voice_db[0], voice_db[1]))
    return voices_from_db_list


def save_persons(persons, cursor):
    ids = []
    for person in persons:
        exist_person = cursor.execute("SELECT * FROM person WHERE name = ?", [person.name]).fetchone()
        if exist_person:
            ids.append(exist_person[0])
            if person.born:
                cursor.execute("UPDATE person SET born = ? WHERE name = ?", (person.born, person.name))
            if person.died:
                cursor.execute("UPDATE person SET died = ? WHERE name = ?", (person.died, person.name))
        else:
            cursor.execute("INSERT INTO person(name, born, died) VALUES (?, ?, ?)",
                           (person.name, person.born, person.died))
            ids.append(cursor.lastrowid)
    return ids


def save_voices(voices, cursor, composition_id):
    index = 1
    for voice in voices:
        exist_voice = cursor.execute("SELECT * FROM voice WHERE number = ? AND score = ?",
                                     (index, composition_id)).fetchone()
        if not exist_voice:
            cursor.execute("INSERT INTO voice(number, score, range, name) VALUES (?, ?, ?, ?)",
                           (index, composition_id, voice.range, voice.name))
        index += 1


main()
