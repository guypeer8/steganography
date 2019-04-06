from lib.binary import pad_zeroes, create_encoded_text_parts
from lib.utils import create_str_parts_array
from os.path import splitext
from math import sqrt, ceil
from PIL import Image
from sys import argv

FILE = 'ocean.jpg'
STEG_FILE = 'steganographic.png'

def convert_image_data(image_data, interceptors = [], iterations=None):
    iterations = len(image_data) if iterations is None else iterations
    for i in range(0, iterations):
        for interceptor in interceptors:
            image_data[i] = tuple(map(interceptor, image_data[i]))

    return image_data

def encode_image(text, file = FILE, steganographic_file = STEG_FILE):
    with Image.open(file) as im:
        if not im.mode == 'RGB': im = im.convert('RGB')

        image_data = list(im.getdata())
        convert_image_data(image_data, [lambda x: pad_zeroes(bin(x))])

        text_parts = create_encoded_text_parts(text)

        while len(text_parts) > 0:
            for i in range(0, len(image_data)):
                image_data[i] = tuple(map(lambda x: (x[:6] + text_parts.pop()) if len(text_parts) > 0 else x, image_data[i]))

        convert_image_data(image_data, [lambda x: int(x, 2)])
        im.putdata(image_data)
        im.save(steganographic_file)

        return len(text)

def decode_image(file = STEG_FILE, text_size = 100):
    with Image.open(file) as im:
        if not im.mode == 'RGB': im = im.convert('RGB')

        image_data = list(im.getdata())
        relevant_image_cells_count = ceil(text_size * 4 / 3) #2 least significant bits encoded for each rgb portion
        text_bits_count = text_size * 8 #number of bits that represent the text
        convert_image_data(image_data, [lambda x: pad_zeroes(bin(x), 2)], iterations=relevant_image_cells_count)

        bit_string = ''
        for i in range(0, relevant_image_cells_count):
            bit_string += ''.join(image_data[i])

        bit_string = bit_string[:text_bits_count] #normalize bit string to text bit size
        bits_array = create_str_parts_array(bit_string, 8)
        decoded_text_array = list(map(lambda x: chr(int(x, 2)), bits_array))

        return ''.join(decoded_text_array)

def get_diff(f1 = FILE, f2 = STEG_FILE):
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
        arguments = argv[1:]
        args_count = len(arguments)
        if args_count == 1 and arguments[0] == '--diff': print(get_diff())
        elif args_count == 2:
            action, value = arguments
            if action == '--encode': print(encode_image(value))
            elif action == '--decode': print(decode_image(text_size=int(value)))
    else:
        print('Please provide arguments')

if __name__ == '__main__':
    main()
