from datagen import *

def matcher(data1, data2, datatotal, toplevel = False):
#    print str(data1) + ' ' + str(data2) + ' ' + str(datatotal)
    combos = []
    if len(datatotal) <= 0:
        return []
    elif len(datatotal) == 1:
        if data1[0] + data2[0] == datatotal[0]:
            return [(data1[0], data2[0], datatotal[0])]
    nprog = 0
    for pt in data1:
        if datatotal[0] - pt in data2:
            matching = (pt, datatotal[0] - pt, datatotal[0])
            data1.remove(pt)
            data2.remove(matching[1])
            matches = matcher(data1, data2, datatotal[1:])
            data1.append(pt)
            data2.append(matching[1])
            combos += [x + matching for x in matches]
        if toplevel:
            nprog += 1
            print ("{}/{} complete".format(nprog, len(data1)))
    return combos

def reformat(combos):
    formatted = []
    for match in combos:
        matchpool = []
        for i in range(0, len(match), 3):
            matchpool.append((match[i], match[i+1], match[i+2]))
        formatted.append(matchpool)
    return formatted

def niceprint(formatted_combos):
    i = 0
    for combo in formatted_combos:
        i += 1
        print "Permutation {}:".format(i)
        for assignment in combo:
            print "\t" + str(assignment)


if __name__ == '__main__':
    l1 = [85, 97, 53, 43, 118, 87, 62, 60, 63, 65]
    l2 = [38, 69, 46, 41, 50, 43, 0, 46, 60, 55]
    lt = groupings(l1, l2)

    l3 = [96, 68, 52, 60, 86, 55, 63, 88, 77, 70, 78, 48, 64, 57, 34, 81, 64, 48, 64, 51, 56, 64, 59, 56, 70, 91, 54, 63, 66, 51]
    l4 = [99, 94, 80, 85, 88, 82, 71, 74, 88, 95, 77, 72, 60, 87, 75, 92, 94, 76, 87, 80, 71, 59, 66, 90, 78, 64, 72, 78, 83, 92]
    lt = groupings(l3, l4)

    l1.sort()
    l2.sort()
    lt.sort()

    print l1, l2, lt

    a = set(matcher(l3, l4, lt, True))
    niceprint(reformat(a))
    print len(a)
