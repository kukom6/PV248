import sys
import csv
import utilities
import numpy
from scipy import stats


def main():
    if len(sys.argv) != 3:
        print("Numbers of parameter are wrong")
    else:
        csv_reader = csv.DictReader(open(sys.argv[1], mode='r'))
        data = utilities.parse_csv_to_dict(csv_reader)
        exercise_data = utilities.merge_exercise_columns(data)
        student_id = float(sys.argv[2])
        points = points_only_for_student(exercise_data, student_id)
        if points is None:
            # TODO average
            sys.stderr.write("Student with id {} doesn't exist!".format(student_id))
            exit(1)
        result={}
        result['mean'] = numpy.mean(points)
        result["median"] = numpy.median(points)
        result["total"] = sum(points)
        result["passed"] = utilities.passed(points)
        #TODO WIP
        slope, intercept, r_value, p_value, std_err = stats.linregress([0], points)
        result["regression slope"] = slope
        utilities.print_dict_as_json(result)


# return list of all points for particular student (particular row for particular student id)
def points_only_for_student(data, student_id):
    index_of_student = -1
    # find student index in array
    for index, value in enumerate(data['student']):
        if value == student_id:
            index_of_student = index
    if index_of_student == -1:
        return None
    result = []
    for column in data:
        if column == 'student':
            continue
        result.append(data[column][index_of_student])
    return result


main()
