def calculate_difference_in_percent(first, second):
    return calculate_difference(first, second) * 100


def calculate_difference(first, second):
    return float((second - first)/first)