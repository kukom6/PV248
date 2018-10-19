import sys
import sqlite3
import import_from_db


# import data from DB to clases and print they to console as from file, diff check integrity of data
# show_data_from_text == show_data_from_db
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
    all_prints_id = cursor.execute("SELECT id FROM print").fetchall()
    for print_id in all_prints_id:
        result_list.append(import_from_db.parse_print(cursor, print_id[0]))
    return result_list


main()
