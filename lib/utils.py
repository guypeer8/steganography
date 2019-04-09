def create_str_parts_array(string, parts=2, is_reversed=False):
    array = [string[i:i + parts] for i in range(0, len(string), parts)]
    if is_reversed:
        array.reverse()

    return array


def join(iterable):
    return ''.join(iterable)
