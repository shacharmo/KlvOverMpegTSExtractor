from .utils import *


def extract_pes(data):
    if len(data) < 3:
        return None
    if read_unsigned_int_be(data, 0, 3) != 1:
        return None

    optional_header = read_unsigned_int_be(data, 6, 2)
    pes = {
        'packet_start_code_prefix': read_unsigned_int_be(data, 0, 3),
        'stream_id': read_unsigned_int_be(data, 3, 1),
        'packet_length': read_unsigned_int_be(data, 4, 2),
        'scrambling_control': zero_fill_right_shift(optional_header & 0x3000, 12),
        'priority': (optional_header & 0x800) != 0,
        'data_alignment_indicator': (optional_header & 0x400) != 0,
        'copyright': (optional_header & 0x200) != 0,
        'original_or_copy': (optional_header & 0x100) != 0,
        'pts_dts_flags': (optional_header & 0xc0) >> 6,
        'escr_flag': (optional_header & 0x20) != 0,
        'sr_rate_flag': (optional_header & 0x10) != 0,
        'dsm_trick_mode_flag': (optional_header & 0x08) != 0,
        'additional_copy_info_flag': (optional_header & 0x04) != 0,
        'crc_flag': (optional_header & 0x02) != 0,
        'extension_flag': (optional_header & 0x01) != 0,
        'header_data_length': read_unsigned_int_be(data, 8, 1)
    }

    if pes['pts_dts_flags'] & 0x2:
        pes['pts'] = get_timestamp(data, 9)

    if pes['pts_dts_flags'] & 0x1:
        pes['dts'] = get_timestamp(data, 14)

    return pes
