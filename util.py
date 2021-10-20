def pair_range(stop_left: int, stop_right: int):
    for i in range(stop_left):
        for j in range(stop_right):
            yield i, j
