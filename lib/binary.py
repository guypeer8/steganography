from .utils import create_str_parts_array, join


def pad_zeroes(s, pad=8):
    s = s.replace('0b', '')
    size = len(s)
    if size > pad:
        return s[-pad:]

    pad_size = pad - size
    while pad_size > 0:
        s = '0' + s
        pad_size -= 1

    return s


def encode_char(char, to_binary=True):
    encoded = char.encode()
    if to_binary:
        integer = encoded[0]
        encoded = pad_zeroes(bin(integer))

    return encoded


def encode_text(text, to_binary=True):
    return join([encode_char(char, to_binary) for char in text])


def create_encoded_text_parts(text, parts=2):
    encoded_text = encode_text(text)
    text_parts = create_str_parts_array(encoded_text, parts, is_reversed=True)
    return text_parts
