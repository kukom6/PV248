import sys
import sqlite3
import json

database = "scorelib.dat"


# show_data_from_text == show_data_from_db
def main():
    if len(sys.argv) != 2:
        print("Numbers of parameter are wrong")
    else:
        print_id = sys.argv[1]
        print_print(print_id)


def print_print(print_id):
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    all_composers = cursor.execute("SELECT person.name, person.born, person.died "
                                   "FROM print JOIN edition JOIN score JOIN score_author JOIN person "
                                   "WHERE print.edition = edition.id AND edition.score = score.id "
                                   "AND score.id = score_author.score AND score_author.composer = person.id "
                                   "AND print.id = ?", (print_id,)).fetchall()
    result = []
    for composer in all_composers:
        result_composer = {'name': composer[0]}
        if composer[1]:
            result_composer['born'] = composer[1]
        if composer[2]:
            result_composer['died'] = composer[2]
        result.append(result_composer)
    print(json.dumps(result, indent=4, ensure_ascii=False))


main()
