import argparse
import klvdata
import mpegtsdata
from klvreconstructor import reconstruct_klv_packets


def extract_klv(path):
    with open(path, 'rb') as stream:
        for packet in klvdata.StreamParser(stream):
            packet.structure()
            packet.validate()


def extract_mpegts(path):
    with open(path, 'rb') as stream:
        streams_packets = mpegtsdata.extract_streams(stream)
    for key in streams_packets:
        packets = streams_packets[key]
        print(f'key=0x{key:X}, packets: {len(packets)}')
        klv_data, total_klv_packets = reconstruct_klv_packets(packets)
        if total_klv_packets:
            print(f'Reconstructed packets: {total_klv_packets}')
            for packet in klvdata.StreamParser(klv_data):
                packet.structure()
                packet.validate()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='File stream to extract', required=True)
    parser.add_argument('-k', '--klv', help='Is file KLV (true) or MPEG-TS (false, default)',
                        default=False, action='store_true')
    args = parser.parse_args()

    if args.klv:
        extract_klv(args.file)
    else:
        extract_mpegts(args.file)
