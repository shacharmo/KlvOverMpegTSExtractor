import argparse
import zlib
import json


def extract_data_capsule(file_path):
    with open(file_path, 'rb') as f:
        buffer = f.read()

    buffer = buffer[4:] # Header
    decoder = zlib.decompressobj(-zlib.MAX_WBITS)
    data = decoder.decompress(buffer)
    data = data[24:-1]
    print('raw', data)
    try:
        json.loads(data)
        print('\nJSON parsed successfully')
    except:
        print('\nFailed to extract JSON!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Data capsule file to extract')
    args = parser.parse_args()

    extract_data_capsule(args.file)
