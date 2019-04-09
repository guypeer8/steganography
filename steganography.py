from lib.binary import pad_zeroes, create_encoded_text_parts
from lib.utils import create_str_parts_array, join
from math import sqrt, ceil
from PIL import Image
from sys import argv

FILE = 'ocean.jpg'
STEG_FILE = 'steganographic.png'
START_INDICATION_PIXELS = 4  # number of pixels used for indicating text size
ENCODING_ERROR = 'Can\'t encode {} characters text on {} pixels rgb image'
ARGUMENTS_INFO = """
Please provide arguments:
  (*) --encode, -e [ text ]
  (*) --decode, -d 
  (*) --diff, -c
""".strip()


# determines how many pixels are needed to encode text when changing the 2 least significant bits
def get_required_pixels_for_text_encoding(text_size):
    return ceil(text_size * 4 / 3)


def is_encodable(text, image_data):
    image_data_size = len(image_data)
    required_image_data_size = get_required_pixels_for_text_encoding(len(text))
    return START_INDICATION_PIXELS + required_image_data_size <= image_data_size


def convert_image_data(image_data, interceptors=[], skip=0, iterations=None):
    image_size = len(image_data)
    iterations = image_size if iterations is None else iterations
    to = min(skip + iterations, image_size)
    for i in range(skip, to):
        for interceptor in interceptors:
            image_data[i] = tuple(map(interceptor, image_data[i]))

    return image_data


def get_encode_conversion_interceptors(parts):
    return [
        lambda x: pad_zeroes(bin(x), 8),
        lambda x: (x[:6] + parts.pop()) if len(parts) > 0 else x,
        lambda x: int(x, 2),
    ]


def get_decode_conversion_interceptors():
    return [lambda x: pad_zeroes(bin(x), 2)]


def encode_image(text, file=FILE, steganographic_file=STEG_FILE):
    with Image.open(file) as im:
        if not im.mode == 'RGB':
            im = im.convert('RGB')

        image_data = list(im.getdata())
        if not is_encodable(text, image_data):
            raise Exception(ENCODING_ERROR.format(len(text), len(image_data)))

        text_size = len(text)

        text_size_binary = pad_zeroes(bin(text_size), 24)
        encoded_text_size_parts = create_str_parts_array(text_size_binary, reversed=True)
        convert_image_data(
            image_data,
            get_encode_conversion_interceptors(encoded_text_size_parts),
            iterations=START_INDICATION_PIXELS,
        )

        text_parts = create_encoded_text_parts(text)
        convert_image_data(
            image_data,
            get_encode_conversion_interceptors(text_parts),
            skip=START_INDICATION_PIXELS,
            iterations=get_required_pixels_for_text_encoding(text_size),
        )

        im.putdata(image_data)
        im.save(steganographic_file)


def decode_image(file=STEG_FILE):
    with Image.open(file) as im:
        if not im.mode == 'RGB':
            im = im.convert('RGB')

        image_data = list(im.getdata())
        decode_interceptors = get_decode_conversion_interceptors()

        convert_image_data(
            image_data,
            decode_interceptors,
            iterations=START_INDICATION_PIXELS,
        )

        start_indicating_bit_string = join([join(image_data[i]) for i in range(0, START_INDICATION_PIXELS)])
        text_size = int(start_indicating_bit_string, 2)

        required_pixels_for_text_encoding = get_required_pixels_for_text_encoding(text_size)
        text_bits_count = text_size * 8  # number of bits that represent the text
        convert_image_data(
            image_data,
            decode_interceptors,
            skip=START_INDICATION_PIXELS,
            iterations=required_pixels_for_text_encoding,
        )

        start, end = START_INDICATION_PIXELS, required_pixels_for_text_encoding + START_INDICATION_PIXELS
        bit_string = join([join(image_data[i]) for i in range(start, end)])
        bit_string = bit_string[:text_bits_count]  # normalize bit string to text bit size
        bits_array = create_str_parts_array(bit_string, 8)
        decoded_text_array = list(map(lambda x: chr(int(x, 2)), bits_array))

        return join(decoded_text_array)


def get_diff(f1=FILE, f2=STEG_FILE):
    with Image.open(f1) as im1:
        with Image.open(f2) as im2:
            image1_data, image2_data = list(map(lambda im: im.getdata(), [im1, im2]))

            diff_factor = 0
            for i in range(0, len(image1_data)):
                r1, g1, b1 = image1_data[i]
                r2, g2, b2 = image2_data[i]
                diff_factor += pow(r1 - r2, 2) + pow(g1 - g2, 2) + pow(b1 - b2, 2)

    return {'pixels': len(image1_data), 'diff': ceil(sqrt(diff_factor))}


def main():
    if len(argv) > 1:
        arguments, args_dict = argv[1:], {}

        args_pairs_list = create_str_parts_array(arguments)
        for args_pair in args_pairs_list:
            args_pair_size = len(args_pair)

            if args_pair_size == 1:
                args_dict[args_pair[0]] = True

            elif args_pair_size == 2:
                arg, value = args_pair
                args_dict[arg] = value

        file, steg_file = FILE, STEG_FILE
        dict_keys = args_dict.keys()

        if '-f' in dict_keys or '--file' in dict_keys:
            file = args_dict.get('-f') or args_dict.get('--file')

        if '-sf' in dict_keys or '--steg-file' in dict_keys:
            steg_file = args_dict.get('-sf') or args_dict.get('--steg-file')

        if '-c' in dict_keys or '--diff' in dict_keys:
            print(get_diff(file, steg_file))

        elif '-d' in dict_keys or '--decode' in dict_keys:
            print(decode_image(steg_file))

        elif '-e' in dict_keys or '--encode' in dict_keys:
            encode_text = args_dict.get('-e') or args_dict.get('--encode')
            encode_image(encode_text, file, steg_file)
    else:
        print(ARGUMENTS_INFO)


if __name__ == '__main__':
    main()
