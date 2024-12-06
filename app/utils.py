def get_hash(prefix, series_of_numbers: list, separator = '-'):

    foo = list()
    foo.append(prefix)
    while len(series_of_numbers) > 0:
        bar = 0
        bar2 = list()
        bar += int(series_of_numbers.pop(0)) + 1
        if len(series_of_numbers) >= 1:
            bar *= int(series_of_numbers.pop())
        if len(series_of_numbers) >= 1:
            bar2.append(series_of_numbers.pop())
            if len(series_of_numbers) >= 1:
                bar2.append(series_of_numbers.pop(0))
            bar *= int(''.join(bar2))
        if len(series_of_numbers) >= 1:
            bar -= int(series_of_numbers.pop())
            if bar < 0:
                bar *= -1
        foo.append(f'{separator}{bar}')

    return ''.join(foo)