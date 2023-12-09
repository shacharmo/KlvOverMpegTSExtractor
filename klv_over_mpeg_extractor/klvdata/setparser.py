#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2017 Matthew Pare (paretech@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pprint import pformat
from abc import ABCMeta
from abc import abstractmethod
from collections import OrderedDict
from klv_over_mpeg_extractor.klvdata.element import Element
from klv_over_mpeg_extractor.klvdata.element import UnknownElement
from klv_over_mpeg_extractor.klvdata.klvparser import KLVParser


class SetParser(Element, metaclass=ABCMeta):
    """Parsable Element. Not intended to be used directly. Always as super class."""
    _unknown_element = UnknownElement

    def __init__(self, value, key_length=1):
        """All parser needs is the value, no other information"""
        super().__init__(self.key, value)
        self.key_length = key_length
        self.items = OrderedDict()
        self.parse()

    def __getitem__(self, key):
        """Return element provided bytes key.

        For consistency of this collection of modules, __getitem__ does not
        attempt to add convenience of being able to index by the int equivalent.
        Instead, the user should pass keys with method bytes.
        """
        return self.items[bytes(key)]

    def parse(self):
        """Parse the parent into items. Called on init and modification of parent value.

        If a known parser is not available for key, parse as generic KLV element.
        """
        for key, value in KLVParser(self.value, self.key_length):
            try:
                self.items[key] = self.parsers[key](value)
            except KeyError:
                self.items[key] = self._unknown_element(key, value)
            except:
                pass  # TODO do something clever

    @classmethod
    def add_parser(cls, obj):
        """Decorator method used to register a parser to the class parsing repertoire.

        obj is required to implement key attribute supporting bytes as returned by KLVParser key.
        """

        # If sublcass of ElementParser does not implement key, dict accepts key of
        # type property object. bytes(obj.key) will raise TypeError. ElementParser
        # requires key as abstract property but no raise until instantiation which
        # does not occur because the value is never recalled and instantiated from
        # parsers.
        cls.parsers[bytes(obj.key)] = obj

        return obj

    @property
    @classmethod
    @abstractmethod
    def parsers(cls):
        # Property must define __getitem__
        pass

    @parsers.setter
    @classmethod
    @abstractmethod
    def parsers(cls):
        # Property must define __setitem__
        pass

    def __repr__(self):
        return pformat(self.items, indent=1)

    def __str__(self):
        return str_dict(self.items)

    def MetadataList(self):
        ''' Return metadata dictionary'''
        metadata = {}

        def repeat(items, indent=1):
            for item in items:
                try:
                    metadata[item.TAG] = (item.LDSName, item.ESDName, item.UDSName, str(item.value.value))
                except:
                    None
                if hasattr(item, 'items'):
                    repeat(item.items.values(), indent + 1)
        repeat(self.items.values())
        return OrderedDict(metadata)

    def custom_repr(self, item):
        return f'{str(type(item))}: {item.value}'

    def structure(self):
        print(self.custom_repr(self))

        def repeat(items, indent=1):
            for item in items:
                print(indent * "\t" + self.custom_repr(item))
                if hasattr(item, 'items'):
                    repeat(item.items.values(), indent+1)

        repeat(self.items.values())

    def validate(self):
        try:
            data = b'\x06\x0e\x2b\x34\x02' + self.key + self.length + self.value
            bcc = 0
            size = len(data) - 2
            for i in range(size):
                bcc += data[i] << (8 * ((i + 1) % 2))

            bcc = bcc & 0xffff
            bcc_value = f'0x{bcc:04X}'
            crc_value = str(self.items[b'\x01'].value)

            is_valid = crc_value == bcc_value
            print(f'Is valid: {is_valid}, Calculated CRC: {bcc_value}, CRC value: {crc_value}')
        except Exception as e:
            print(f'Cannot validate: {e}')


def str_dict(values):
    out = []

    def per_item(value, indent=0):
        for item in value:
            if isinstance(item):
                out.append(indent * "\t" + str(item))
            else:
                out.append(indent * "\t" + str(item))

    per_item(values)

    return '\n'.join(out)
