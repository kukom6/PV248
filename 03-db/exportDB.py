import sys
import scorelib
import sqlite3


# import data from DB to clases and print they to console as from file, diff check integrity of data
def main():
    if len(sys.argv) != 2:
        print("Numbers of parameter are wrong")
    else:
        list_of_prints = from_db(sys.argv[1])
        for content in list_of_prints:
            content.format()
            print()


def from_db(database):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    result = parse_print(cursor)
    cursor.close()
    return result


def parse_print(cursor):
    result_list = []
    all_prints = cursor.execute("SELECT id, partiture, edition FROM print").fetchall()
    for print in all_prints:
        print_id = print[0]
        edition_id = print[2]
        edition = parse_edition(cursor, edition_id)
        partiture = print[1] == 'Y'
        result_print = scorelib.Print(edition, print_id, partiture)
        result_list.append(result_print)
    return result_list


def parse_edition(cursor, edition_id):
    edition = cursor.execute("SELECT score, name FROM edition WHERE edition.id=?", (edition_id,)).fetchone()
    composition_id = edition[0]
    edition_name = edition[1]
    authors = parse_authors(cursor, edition_id)
    composition = parse_composition(cursor, composition_id)
    return scorelib.Edition(composition, authors, edition_name)


def parse_composition(cursor, composition_id):
    composition = cursor.execute("SELECT name, genre, key, incipit, year FROM score WHERE score.id=?",
                                 (composition_id,)).fetchone()
    composition_name = composition[0]
    composition_genre = composition[1]
    composition_key = composition[2]
    composition_incipit = composition[3]
    composition_year = composition[4]
    composition_composers = parse_composers(cursor, composition_id)
    composition_voices = parse_voices(cursor, composition_id)
    return scorelib.Composition(composition_name, composition_incipit, composition_key, composition_genre,
                                composition_year, composition_voices, composition_composers)


def parse_voices(cursor, composition_id):
    result = []
    voices = cursor.execute("SELECT range, name FROM voice WHERE voice.score=? ORDER BY voice.number ASC",
                            (composition_id,)).fetchall()
    for voice in voices:
        voice_name = voice[1]
        voice_range = voice[0]
        result.append(scorelib.Voice(voice_name, voice_range))
    return result


def parse_authors(cursor, edition_id):
    authors = cursor.execute("SELECT person.name, person.born, person.died FROM edition JOIN edition_author JOIN person"
                             " WHERE edition.id=edition_author.edition AND person.id=edition_author.editor "
                             "AND edition.id=?", (edition_id,)).fetchall()

    return parse_people(authors)


def parse_composers(cursor, composition_id):
    compositors = cursor.execute("SELECT person.name, person.born, person.died FROM score JOIN score_author JOIN person"
                                 " WHERE score.id=score_author.score AND person.id=score_author.composer "
                                 "AND score.id=?", (composition_id,)).fetchall()
    return parse_people(compositors)


def parse_people(list_people):
    result = []
    for people in list_people:
        people_name = people[0]
        people_born = people[1]
        people_died = people[2]
        result.append(scorelib.Person(people_name, people_born, people_died))
    return result


main()
