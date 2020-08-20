import binascii
import klvdata

universal_key = binascii.unhexlify('060e2b34020b0101')


def reconstruct_klv_packets(packets):
    """
    Reconstruct KLV packets from TS packets
    :param packets: MPEG-TS packets
    :return: Buffer containing the KLV payload, list of pts per packet
    """
    is_found = False
    buffer = b''
    i_buffer = b''
    pts_per_packet = []
    start_indicators = 0

    for packet in packets:
        if packet["payload_unit_start_indicator"]:
            start_indicators += 1
            if is_found and len(i_buffer):
                for x in klvdata.StreamParser(i_buffer):
                    print('intm start')
                    x.structure()
                    x.validate()
                    print('intm end')
                i_buffer = ''
            is_found = universal_key in packet['payload']
            if is_found:
                pts_per_packet.append(packet['pes']['pts'] if ('pes' in packet and 'pts' in packet['pes']) else None)
                key_index = packet['payload'].index(universal_key)
                buffer += packet['payload'][key_index:]
                i_buffer = packet['payload'][key_index:]
        elif is_found:
            buffer += packet['payload']
            i_buffer += packet['payload']
    print(f'Total packets: {len(packets)}, Start indicator: {start_indicators}')
    return buffer, pts_per_packet
