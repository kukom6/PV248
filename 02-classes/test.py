import sys
import scorelib


def main():
    if len(sys.argv) != 2:
        print("Numbers of parameter are wrong")
    else:
        list_of_prints = scorelib.load(sys.argv[1])
        for content in list_of_prints:
            content.format()


main()
