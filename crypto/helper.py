def calculate_difference_in_percent(first, second):
    return calculate_difference(first, second) * 100


def calculate_difference(first, second):
    if first != 0:
        return float((second - first)/first)
    else:
        return float((second - first))