import sys
import scorelib


def main():
    if len(sys.argv) != 2:
        print("Numbers of parameter are wrong")
    else:
        list = scorelib.load(sys.argv[1])  # TODO
        for content in list:
            print("------------------------------------------------------------------")
            print(content)

main()
