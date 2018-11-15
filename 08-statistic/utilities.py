import copy
import json


# Parse CSV to dictionary
def parse_csv_to_dict(csv_reader):
    result = {}
    # field name init
    for field_name in csv_reader.fieldnames:
        result[field_name] = []
    # add data to dist
    for row in csv_reader:
        for key in row:
            result[key].append(float(row[key]))
    return result


# Merge column according date, e.g. 1.1.2018/1 1.1.2018/2 merge (sum values) into one column 1.1.2018
def merge_date_columns(data):
    result = {}
    for originalColumn in data:
        if originalColumn == 'student':
            result['student'] = copy.deepcopy(data['student'])
            continue
        date = originalColumn.split("/")[0]
        if date not in result.keys():
            result[date] = copy.deepcopy(data[originalColumn])
        else:  # date is already in result
            for index, cell in enumerate(data[originalColumn]):
                result[date][index] += cell
    return result


# Merge column according exercise, e.g. 1.1.2018/2 7.1.2018/2 merge (sum values) into one column 2
def merge_exercise_columns(data):
    result = {}
    for originalColumn in data:
        if originalColumn == 'student':
            result['student'] = copy.deepcopy(data['student'])
            continue
        exercise = originalColumn.split("/")[1]
        if exercise not in result.keys():
            result[exercise] = copy.deepcopy(data[originalColumn])
        else:  # exercise is already in result
            for index, cell in enumerate(data[originalColumn]):
                result[exercise][index] += cell
    return result


# How many passed
def passed(array):
    result = 0
    for value in array:
        if value > 0:
            result += 1
    return result


# For manage this print in one place of code
def print_dict_as_json(dictionary):
    print(json.dumps(dictionary, indent=4, ensure_ascii=False))
