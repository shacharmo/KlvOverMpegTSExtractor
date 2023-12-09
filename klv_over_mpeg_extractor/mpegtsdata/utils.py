def zero_fill_right_shift(val, n):
    return (val >> n) if val >= 0 else ((val + 0x100000000) >> n)


def read_unsigned_int32_be(data, index):
    return int.from_bytes(data[index:index + 4], byteorder='big', signed=False)


def read_unsigned_int_be(data, index, length):
    return int.from_bytes(data[index:index + length], byteorder='big', signed=False)


def is_packet_start(data):
    return data[0] == 0x47


def get_timestamp(data, index):
    timestamp = (read_unsigned_int_be(data, index, 1) & 0x0E) * 536870912
    timestamp += (read_unsigned_int_be(data, index + 1, 2) & 0xFFFE) * 16384
    timestamp += int(read_unsigned_int_be(data, index + 3, 2) / 2)
    return timestamp


def get_or_create_key(dict, key, default_value):
    if key in dict:
        value = dict[key]
    else:
        value = default_value
        dict[key] = value
    return value
