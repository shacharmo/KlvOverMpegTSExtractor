import click
from klv_over_mpeg_extractor import mpegtsdata, klvdata
from klv_over_mpeg_extractor.klvreconstructor import reconstruct_klv_packets


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


@click.command()
@click.option("--file", "-f", help="File stream to extract", type=str)
@click.option("--klv", "-k", help='Is file KLV (true) or MPEG-TS (false)', is_flag=True)
def klv_extractor(file: str, klv: bool):
    if klv:
        extract_klv(file)
    else:
        extract_mpegts(file)
