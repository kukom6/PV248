import sys
import re
from collections import Counter


def composer(file):
    ctr = Counter()
    for line in file:
        r = re.compile(r"Composer: (.+)")
        m = r.match(line)
        if m is None:
            continue
        line_names = m.group(1).split(';')
        for name in line_names:
            # only characters (with diacritics too), space and comma if there are more authors
            filtered_name = re.sub(r"[^A-Za-z\u00c0-\u017F ,]", '', name)
            ctr[filtered_name.strip()] += 1  # strip(), some authors has space after name
    for k, v in ctr.most_common():  # sorted by values
        print("%s: %d" % (k, v))


def century(file):
    ctr = Counter()
    for line in file:
        r = re.compile(r"Composition Year: .*[0-9]+.*")
        m = r.match(line)
        if m is None:
            continue  # not a composition year line
        year = re.search(r"[1-9][0-9][0-9][0-9]", m.group(0))
        if year is None:  # try another format
            cent_string = re.search(r"[1-9][0-9]th", m.group(0))
            if cent_string is None:
                continue
            cent = int(cent_string.group(0).rstrip("th"))
            ctr[cent] += 1
        else:
            cent = int(year.group(0)[:2]) + 1  # only first two digit are needed + correct century (+1)
            ctr[cent] += 1
    for k, v in sorted(ctr.items()):
        print("%sth century: %d" % (k, v))


def main():
    file = open(sys.argv[1], 'r', encoding='UTF8')
    mode = sys.argv[2]

    if mode == "century":
        century(file)
    elif mode == "composer":
        composer(file)
    else:
        print("Unsupported mode")


main()
