import sys
import sqlite3
import json
import import_from_db

database = "scorelib.dat"


def main():
    if len(sys.argv) != 2:
        print("Numbers of parameter are wrong")
    else:
        composer_sub = sys.argv[1]
        search(composer_sub)


def search(composer_sub):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    all_composers = cursor.execute("SELECT person.id, person.name FROM person "
                                      "WHERE person.name LIKE ?", ("%" + composer_sub + "%",)).fetchall()
    result = {}
    for composer in all_composers:
        composer_name = composer[1]
        result[composer_name] = search_prints_for_composer(cursor, composer[0])
    print(json.dumps(result, indent=4, ensure_ascii=False))
    cursor.close()


def search_prints_for_composer(cursor, composer_id):
    prints_id = cursor.execute("SELECT DISTINCT print.id "
                               "FROM print JOIN edition JOIN score JOIN score_author JOIN person "
                               "WHERE print.edition = edition.id AND edition.score = score.id "
                               "AND score.id = score_author.score AND score_author.composer = person.id "
                               "AND person.id = ?", (composer_id,)).fetchall()
    list_prints = []
    for print_id in prints_id:
        print_object = import_from_db.parse_print(cursor, print_id[0])  # return print Object for particular print_id
        list_prints.append(parse_print_object_to_dictionary(print_object))
    return list_prints


# convert print object to dictionary for JSON parsing according to ORIGINAL pattern from .txt
def parse_print_object_to_dictionary(print_object):
    result = {}
    result['Print Number'] = print_object.print_id
    result['Composer'] = parse_people_list_to_dictonary(print_object.edition.composition.authors)
    if print_object.edition.composition.name:
        result['Title'] = print_object.edition.composition.name
    if print_object.edition.composition.genre:
        result['Genre'] = print_object.edition.composition.genre
    if print_object.edition.composition.key:
        result['Key'] = print_object.edition.composition.key
    if print_object.edition.composition.year:
        result['Composition Year'] = print_object.edition.composition.year
    # result['Publication Year'] =
    if print_object.edition.name:
        result['Edition'] = print_object.edition.name
    result['Editor'] = parse_people_list_to_dictonary(print_object.edition.authors)
    result['Voices'] = parse_voices_list_to_dictonary(print_object.edition.composition.voices)
    if print_object.partiture:
        result['Partiture'] = 'Y' if print_object.partiture else 'N'
    if print_object.edition.composition.incipit:
        result['Incipit'] = print_object.edition.composition.incipit
    return result


def parse_people_list_to_dictonary(authors):
    result = []
    for author in authors:
        result_author = {}
        result_author['name'] = author.name
        if author.born:
            result_author['born'] = author.born
        if author.died:
            result_author['died'] = author.died
        result.append(result_author)
    return result


def parse_voices_list_to_dictonary(voices):
    result = {}
    counter = 1
    for voice in voices:
        result_voice = {}
        if voice.name:
            result_voice['name'] = voice.name
        if voice.range:
            result_voice['range'] = voice.range
        result[counter] = result_voice
        counter += 1
    return result


main()
