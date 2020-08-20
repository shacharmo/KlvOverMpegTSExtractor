import argparse
import klvdata
import mpegtsdata
from klvreconstructor import reconstruct_klv_packets


def extract_klv(path):
    with open(path, 'rb') as stream:
        for packet in klvdata.StreamParser(stream):
            packet.structure()
            packet.validate()


def extract_mpegts(path, data_capsule_base_file, print_data_capsule):
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
        if key == 257 and (print_data_capsule or data_capsule_base_file):
            buffer = b''
            is_found = False
            counter = 0
            total = 0
            pesCount = 0
            for packet in packets:
                total += 1
                has_pes = 'pes' in packet and packet['pes']
                if has_pes:
                    pesCount += 1
                    idx = packet['pes']['data_index']
                else:
                    idx = 0
                if packet['payload_unit_start_indicator']:
                    pes_data = ''.join('{:02x}'.format(x) for x in packet['payload'][:idx])
                    bin_data = ''.join('{:02x}'.format(x) for x in packet['payload'][idx:])
                    if print_data_capsule:
                        print('START', idx, len(packet['payload'][idx:]), counter, pes_data, bin_data, packet)
                    if not is_found:
                        is_found = True
                    else:
                        counter += 1
                        if data_capsule_base_file:
                            with open(f'{data_capsule_base_file}.{counter}', 'wb') as f:
                                f.write(buffer)
                            buffer = b''
                elif print_data_capsule: print('DX', idx, len(packet['payload'][idx:]))
                if is_found and data_capsule_base_file: buffer += packet['payload'][idx:]
            if len(buffer):
                counter += 1
                if data_capsule_base_file:
                    with open(f'{data_capsule_base_file}.{counter}', 'wb') as f:
                        f.write(buffer)
            if print_data_capsule:
                print('pes count', pesCount)
                print('counter', counter, 'total', total)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='File stream to extract', required=True)
    parser.add_argument('-k', '--klv', help='Is file KLV (true) or MPEG-TS (false, default)',
                        default=False, action='store_true')
    parser.add_argument('-d', '--datacapsule', help='File base to output payload of data capsules')
    parser.add_argument('-p', '--printcapsule', help='Is print data capsule info',
                        default=False, action='store_true')
    args = parser.parse_args()

    if args.klv:
        extract_klv(args.file)
    else:
        extract_mpegts(args.file, args.datacapsule, args.printcapsule)
