from .adaptaionfield import *
from .pes import *
from .utils import *


def extract_packet(data):
    if not is_packet_start(data):
        return None
    packet = {
        'sync_byte': data[0],
        'transport_error_indicator': zero_fill_right_shift(data[1] & 0x80, 7),
        'payload_unit_start_indicator': zero_fill_right_shift(data[1] & 0x40, 6),
        'transport_priority': zero_fill_right_shift(data[1] & 0x20, 5),
        'packet_id': ((data[1] & 0x1F) << 8) | data[2],
        'transport_scrambling_control': zero_fill_right_shift(data[3] & 0xC0, 6),
        'adaptation_field_control': zero_fill_right_shift(data[3] & 0x30, 4),
        'continuity_counter': data[3] & 0x0F,
        'payload_index': len(data)
    }

    field_control = packet['adaptation_field_control']
    if (field_control == 0x02) or (field_control == 0x03):  # Adaptation field
        packet['adaptation_field'] = extract_adaptation_field(data)

    if field_control == 0x01:
        packet['payload_index'] = 4
    elif field_control == 0x03:
        packet['payload_index'] = 5 + packet['adaptation_field']['field_length']

    if packet['payload_index'] > len(data):
        print(f'Packet has payload start bigger then length: {packet["payload_index"]} >= {len(data)}')

    packet['payload'] = data[packet['payload_index']:]
    packet['pes'] = extract_pes(packet['payload'])
    return packet
