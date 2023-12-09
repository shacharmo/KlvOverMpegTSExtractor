from .utils import *


def extract_adaptation_optional_fields(data, field):
    index = 6
    optional_fields = {}

    if field['pcr_flag']:
        optional_fields['pcr_base'] = read_unsigned_int32_be(data, index) * 2 + \
                                      zero_fill_right_shift(data[index + 4] & 0x80, 7)
        optional_fields['pcr_extension'] = (data[index + 4] & 0x1 << 8) + data[index + 5]
        index += 6

    if field['opcr_flag']:
        optional_fields['opcr_base'] = read_unsigned_int32_be(data, index) * 2 + \
                                       zero_fill_right_shift(data[index + 4] & 0x80, 7)
        optional_fields['opcr_extension'] = (data[index + 4] & 0x1 << 8) + data[index + 5]
        index += 6

    if field['splicing_point_flag']:
        optional_fields['splice_countdown'] = data[index]
        index += 1

    if field['transport_private_data_flag']:
        optional_fields['transport_private_data_length'] = data[index]
        optional_fields['private_data'] = None  # TODO
        index += 1 + field['transport_private_data_flag']

    # TODO extract other fields

    return optional_fields


def extract_adaptation_field(data):
    length = data[4]

    if length <= 0:
        return {'field_length': length}

    field = {
        'field_length': length,
        'discontinuity_indicator': zero_fill_right_shift(data[5] & 0x80, 7),
        'random_access_indicator': zero_fill_right_shift(data[5] & 0x40, 6),
        'elementary_stream_priority_indicator': zero_fill_right_shift(data[5] & 0x20, 5),
        'pcr_flag': zero_fill_right_shift(data[5] & 0x10, 4),
        'opcr_flag': zero_fill_right_shift(data[5] & 0x08, 3),
        'splicing_point_flag': zero_fill_right_shift(data[5] & 0x04, 2),
        'transport_private_data_flag': zero_fill_right_shift(data[5] & 0x02, 1),
        'adaptation_field_extension_flag': data[5] & 0x01
    }
    field['optional_fields'] = extract_adaptation_optional_fields(data, field)
    return field
