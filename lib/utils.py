def create_str_parts_array(string, parts):
    return [string[i:i + parts] for i in range(0, len(string), parts)]