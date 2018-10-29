import numpy
import sys
import re


def main():
    if len(sys.argv) != 2:
        print("Numbers of parameter are wrong")
    else:
        file = open(sys.argv[1], 'r', encoding='UTF8').read()
        constants = []
        # find all variables in the file and add it to the dictionary
        matrix_dict = find_all_variables_and_initial_matrix(file)
        lines_in_file = file.split("\n")
        for line in lines_in_file:
            if '=' not in line:
                continue  # invalid line
            split_line = line.split('=')
            constants.append(int(split_line[1].strip()))  # right side is always constant
            left_side_without_spaces = "".join(split_line[0].split())
            # find all number groups e.g. "2x+4y-2z" -> three group "2x" "4y" "-2z"
            founded_group = re.findall(r"([+,\-]?\d*\w{1})", left_side_without_spaces)
            if founded_group is None:
                continue
            # parsing group of number
            for group in founded_group:
                parsed_group = re.search(r"([+,\-]?)(\d*)(\w)", group)  # "-50y"
                result = 1
                if parsed_group.group(1) is '-':
                    result *= -1
                if parsed_group.group(2) is not '':
                    result *= int(parsed_group.group(2))
                if parsed_group.group(3) not in matrix_dict.keys():
                    sys.stderr("Founded variables which is not in the matrix. Variable: '" + str(parsed_group.group(3))
                               + "' matrix keys: " + str(matrix_dict.keys()))
                else:
                    matrix_dict[parsed_group.group(3)].append(result)
            # add zero to variables which are not in this line
            add_zero_to_variables(matrix_dict)
        matrix = convert_dict_matrix_to_matrix(matrix_dict)
        # final matrix
        numpy_matrix = numpy.array(matrix)
        numpy_constant = numpy.array(constants)
        rank_matrix = numpy.linalg.matrix_rank(numpy_matrix)
        rank_with_constant = numpy.linalg.matrix_rank(numpy.column_stack((numpy_matrix, numpy_constant)))
        if rank_matrix != rank_with_constant:
            print("no solution")
        elif rank_matrix < len(matrix_dict.items()):  # number of variables
            print("solution space dimension:", len(matrix_dict.items()) - rank_matrix)
        else:
            solved = numpy.linalg.solve(numpy_matrix, numpy_constant)
            i = 0
            results = []
            # need to be sorted to keep the contract
            for key in sorted(matrix_dict.keys()):
                results.append(key + " = " + str(solved[i]))
                i += 1
            print("solution: " + ", ".join(results))


# because matrix is save in dictionary by variables like x, y, z. For each variable is array which contains
# value according to line (index == line )
# e.g.
# 1x+4y
# 2x+5y
# 3x+6y
# input: dictionary:
# x: [1,2,3]
# y: [4,5,6]
# output: convert to matrix:
# [[1,4][2,5][3,6]]
def convert_dict_matrix_to_matrix(matrix_dict):
    matrix = []
    number_of_row = max([len(v) for v in matrix_dict.values()])
    for i in range(0, number_of_row):
        row = []
        # need to sort by variable because y can be first (before x) in the dictionary
        for key in sorted(matrix_dict.keys()):
            row.append(matrix_dict[key][i])
        matrix.append(row)
    return matrix


def find_all_variables_and_initial_matrix(file):
    matrix = {}
    founded_letters = re.findall(r"([A-Za-z]{1})", file)
    for letter in founded_letters:
        if letter not in matrix.keys():
            matrix[letter] = []
    return matrix


# when variable is not in the line, add 0 to the matrix
def add_zero_to_variables(matrix):
    maximum_len = max((len(variables) for key, variables in matrix.items()))
    for key, variables in matrix.items():
        if len(variables) < maximum_len:
            variables.append(0)


main()
