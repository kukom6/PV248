import sys
import scorelib
import sqlite3

sql_schema = open("./scorelib.sql", 'r', encoding='UTF8').read()


def main():
    if len(sys.argv) != 3:
        print("Numbers of parameter are wrong")
    else:
        toDb(scorelib.load(sys.argv[1]))


def toDb(prints):
    connection = sqlite3.connect(sys.argv[2])
    cursor = connection.cursor()
    cursor.execute("DROP TABLE person")
    cursor.execute("DROP TABLE score")
    cursor.execute("DROP TABLE voice")
    cursor.execute("DROP TABLE edition")
    cursor.execute("DROP TABLE score_author")
    cursor.execute("DROP TABLE edition_author")
    cursor.execute("DROP TABLE print")

    table_exist = cursor.execute("SELECT name "
                                 "FROM sqlite_master "
                                 "WHERE type='table' "
                                 "AND name IN ('person','score','voice','editio','score','author','edition','author','print');").fetchall()
    if not table_exist:
        cursor.executescript(sql_schema)

    for one_print in prints:
        save_print(one_print, cursor)

    cursor.close()
    connection.commit()


def save_print(print, cursor):
    id_edition = save_edition(print.edition, cursor)
    cursor.execute("INSERT INTO print (id, partiture, edition) VALUES (?, ?, ?)",
                   (print.print_id, 'Y' if print.partiture else 'N', id_edition))


def save_edition(edition, cursor):
    id_compostion = save_composition(edition.composition, cursor)
    exist_edition = cursor.execute("SELECT * FROM edition WHERE name = ?", (edition.name,)).fetchone()
    # TODO join
    if exist_edition:
        edition_id = exist_edition[0]
    else:
        cursor.execute("INSERT INTO edition (score, name, year) VALUES (?, ?, ?)",
                       (id_compostion, edition.name, None))
        edition_id = cursor.lastrowid

    # Save person and create connection M:N
    ids_authors = save_persons(edition.authors, cursor)
    for id_author in ids_authors:
        exist_connection = cursor.execute("SELECT * FROM edition_author WHERE edition = ? AND editor = ?",
                                          (edition_id, id_author))
        if exist_connection:
            cursor.execute("INSERT INTO edition_author (edition, editor) VALUES (?, ?)", (edition_id, id_author))

    return edition_id


# save compostion method, method check whether composition is not in the db, but not only on score table but also
# on person and voice table, because two composition are same only when authors(persons) and voices are same too
def save_composition(composition, cursor):
    exist_composition = cursor.execute("SELECT * FROM score WHERE "
                                       "name IS ? AND genre IS ? AND key IS ? AND incipit IS ? AND year IS ?",
                                       (composition.name, composition.genre, composition.key, composition.incipit,
                                        composition.year)).fetchall()
    if exist_composition:
        #  composition exist in db but it might not be same because authors and voices can be different
        composition_id = exist_composition[0]
        composers_name_for_this_composition = cursor.execute("SELECT person.name FROM score_author JOIN person "
                                                             "WHERE score_author.score = ? AND "
                                                             "score_author.composer=person.id",
                                                             (composition_id,)).fetchall()
        voices_for_this_composition = cursor.execute(
            "SELECT voice.name, voice.range FROM voice WHERE voice.score = ?", (composition_id,)).fetchall()
        if not same_persons(composition.authors, composers_name_for_this_composition) \
                or not same_voices(composition.voices, voices_for_this_composition):
            # compostion has different compositors or voices
            cursor.execute("INSERT INTO score (name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)",
                        (composition.name, composition.genre, composition.key, composition.incipit, composition.year))
            composition_id = cursor.lastrowid
    else:
        cursor.execute("INSERT INTO score (name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)",
                       (composition.name, composition.genre, composition.key, composition.incipit, composition.year))
        composition_id = cursor.lastrowid

    save_voices(composition.voices, cursor, composition_id)
    # connect M:N
    ids_authors = save_persons(composition.authors, cursor)
    for id_author in ids_authors:
        exist_connection = cursor.execute("SELECT * FROM score_author WHERE score = ? AND composer = ?",
                                          (composition_id, id_author))
        if exist_connection:
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
            if person.born:
                cursor.execute("UPDATE person SET born = ? WHERE name = ?", (person.born, person.name))
            if person.died:
                cursor.execute("UPDATE person SET died = ? WHERE name = ?", (person.died, person.name))
            ids.append(cursor.lastrowid)
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
