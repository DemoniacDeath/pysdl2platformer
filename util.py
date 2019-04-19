def pairRange(stopL: int, stopR: int):
    for i in range(stopL):
        for j in range(stopR):
            yield (i, j)
