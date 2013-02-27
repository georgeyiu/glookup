import random

def distribution(numpts, mean = 70, stddev = 15):
    data = []
    for i in range(numpts):
        data.append(int(random.gauss(mean, stddev)))
    return data

def groupings(dist1, dist2):
    return [dist1[i] + dist2[i] for i in range(len(dist1))]

