import argparse
import shutil
import subprocess
import sys
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
        klv_data, pts_per_packet = reconstruct_klv_packets(packets)
        total_klv_packets = len(pts_per_packet)
        if total_klv_packets:
            print(f'Reconstructed packets: {total_klv_packets}')
            index = 0
            for packet in klvdata.StreamParser(klv_data):
                print(f'Packet pts: {pts_per_packet[index]}')
                index += 1
                packet.structure()
                packet.validate()


def validate(path):
    """Validate the file's KLV metadata with misb-check, when available.

    Works on both MPEG-TS and extracted KLV binary files, independently of
    the extraction above. Returns the misb-check exit code, or 0 when the
    binary is not installed.
    """
    misb_check = shutil.which('misb-check')
    if misb_check is None:
        print('misb-check not found on PATH, skipping validation.')
        print('Install it with: cargo install misb')
        return 0
    print(f'Validating {path} with misb-check...', flush=True)
    return subprocess.run([misb_check, path]).returncode


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='File stream to extract', required=True)
    parser.add_argument('-k', '--klv', help='Is file KLV (true) or MPEG-TS (false, default)',
                        default=False, action='store_true')
    parser.add_argument('-v', '--validate', help='Validate KLV metadata with misb-check '
                        '(https://crates.io/crates/misb) before extraction',
                        default=False, action='store_true')
    args = parser.parse_args()

    exit_code = validate(args.file) if args.validate else 0

    if args.klv:
        extract_klv(args.file)
    else:
        extract_mpegts(args.file)

    sys.exit(exit_code)
