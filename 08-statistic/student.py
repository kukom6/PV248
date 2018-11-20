import sys
import csv
import utilities
import numpy
from datetime import datetime
from datetime import timedelta

date_format = "%Y-%m-%d"
start_semester = datetime.strptime('2018-09-17', date_format)


def main():
    if len(sys.argv) != 3:
        print("Numbers of parameter are wrong")
    else:
        csv_reader = csv.DictReader(open(sys.argv[1], mode='r'))
        data = utilities.parse_csv_to_dict(csv_reader)
        student_id = sys.argv[2]

        exercise_data = points_only_for_student(utilities.merge_exercise_columns(data), student_id)
        if exercise_data is None:
            sys.stderr.write("Student with id {} doesn't exist!".format(student_id))
            exit(1)

        result={}
        result['mean'] = numpy.mean(exercise_data)
        result["median"] = numpy.median(exercise_data)
        result["total"] = sum(exercise_data)
        result["passed"] = utilities.passed(exercise_data)

        points_per_day = points_only_for_student(utilities.merge_date_columns(data), student_id)
        accumulated_points = numpy.cumsum(points_per_day)
        diff_from_start_semester = get_date_diff_from_start(data)

        # 1D -> 2D array; (https://stackoverflow.com/questions/12575421/convert-a-1d-array-to-a-2d-array-in-numpy )
        # due to exception Array must be two-dimensional
        a = numpy.expand_dims(numpy.array(diff_from_start_semester), axis=1)
        b = numpy.array(accumulated_points)

        slope = numpy.linalg.lstsq(a, b, rcond=1)[0][0]
        result["regression slope"] = slope
        if slope > 0:
            date_to_16 = compute_date_to_point(16, slope)
            date_to_20 = compute_date_to_point(20, slope)
            result["date 16"] = date_to_16.strftime("%Y-%m-%d")
            result["date 20"] = date_to_20.strftime("%Y-%m-%d")
        utilities.print_dict_as_json(result)


# return list of all points for particular student (particular row for particular student id)
def points_only_for_student(data, student_id):
    index_of_student = -1
    if student_id != 'average':
        # find student index in array
        student_id = float(student_id)
        for index, value in enumerate(data['student']):
            if value == student_id:
                index_of_student = index
        if index_of_student == -1:
            return None  # not average and student doesn't exist
    result = []
    for column_name in data:
        if column_name == 'student':
            continue
        if index_of_student == -1:
            average_for_column = numpy.mean(data[column_name])
            result.append(average_for_column)
        else:
            result.append(data[column_name][index_of_student])
    return result


# https://stackoverflow.com/questions/151199/how-do-i-calculate-number-of-days-between-two-dates-using-python
def get_date_diff_from_start(data):
    result = []
    dates = []
    for originalColumn in data:
        if originalColumn == 'student':
            continue
        date = originalColumn.split("/")[0]
        if date not in dates:
            dates.append(date)
    for date in dates:
        curr_date = datetime.strptime(date, date_format)
        delta = curr_date - start_semester
        result.append(delta.days)
    return result


# compute how many day is needed to reach the point from the start date
# https://stackoverflow.com/questions/6871016/adding-5-days-to-a-date-in-python
def compute_date_to_point(point, slope):
    date_diff_from_start = point / slope
    return start_semester + timedelta(days=date_diff_from_start)


main()
