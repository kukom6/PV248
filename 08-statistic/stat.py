import sys
import csv
import json
import numpy
import utilities


def main():
    if len(sys.argv) != 3:
        print("Numbers of parameter are wrong")
    else:
        csv_reader = csv.DictReader(open(sys.argv[1], mode='r'))
        data = utilities.parse_csv_to_dict(csv_reader)
        mode = sys.argv[2]
        if mode == 'dates':
            print(json.dumps(dates(data), indent=4, ensure_ascii=False))
        elif mode == 'deadlines':
            print(json.dumps(deadlines(data), indent=4, ensure_ascii=False))
        elif mode == 'exercises':
            print(json.dumps(exercises(data), indent=4, ensure_ascii=False))
        else:
            print("{} mode is unsupported".format(mode))


def dates(data):
    merged_data = utilities.merge_date_columns(data)
    return create_dict_for_print(merged_data)


def deadlines(data):
    return create_dict_for_print(data)


def exercises(data):
    merged_data = utilities.merge_exercise_columns(data)
    return create_dict_for_print(merged_data)


def passed(array):
    result = 0
    for value in array:
        if value > 0:
            result += 1
    return result


# Create dictionary for output
def create_dict_for_print(data):
    result = {}
    for column in data:
        if column == 'student':
            continue
        result[column] = {}
        result[column]["mean"] = numpy.mean(data[column])
        result[column]["median"] = numpy.median(data[column])
        result[column]["first"] = numpy.percentile(data[column], 25)
        result[column]["last"] = numpy.percentile(data[column], 75)
        result[column]["passed"] = passed(data[column])
    return result





main()
