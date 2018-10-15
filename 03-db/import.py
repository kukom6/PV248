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
    return cursor.lastrowid

#     TODO


def save_edition(edition, cursor):
    id_compostion = save_composition(edition.composition, cursor)
    ids_authors = save_persons(edition.authors, cursor)
#     TODO
    return cursor.lastrowid


def save_composition(composition, cursor):
    ids_authors = save_persons(composition.authors, cursor)
    ids_voices = save_voices(composition.voices, cursor)
    return cursor.lastrowid
#     TODO


def save_persons(persons, cursor):
    ids = []
    for person in persons:
        exist_person = cursor.execute("SELECT * FROM person WHERE name = ?", [person.name]).fetchall()
        if exist_person:
            if person.born:
                cursor.execute("UPDATE person SET born = ? WHERE name = ?", (person.born, person.name))
            if person.died:
                cursor.execute("UPDATE person SET died = ? WHERE name = ?", (person.died, person.name))
            ids.append(cursor.lastrowid)
        else:
            cursor.execute("INSERT INTO person(name, born, died) VALUES (?, ?, ?)", (person.name, person.born, person.died))
            ids.append(cursor.lastrowid)
    return cursor.lastrowid


def save_voices(voices, cursor):
    return cursor.lastrowid


main()
