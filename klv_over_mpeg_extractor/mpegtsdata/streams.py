from .packet import extract_packet
from .utils import get_or_create_key

packet_size = 188


def extract_streams(stream):
    """
    Extract MPEG-TS packets per stream
    :param stream: MPEG-TS data stream, usually from a file
    :return: Dictionary of stream id (key) and list of packets (value)
    """
    streams_packets = {}
    packet_data = stream.read(packet_size)
    while packet_data:
        packet = extract_packet(packet_data)
        stream_packets = get_or_create_key(streams_packets, packet['packet_id'], [])
        stream_packets.append(packet)
        packet_data = stream.read(packet_size)
    return streams_packets
