import random

def distribution(numpts, mean = 70, stddev = 15):
    data = []
    for i in range(numpts):
        data.append(int(random.gauss(mean, stddev)))
    return data
