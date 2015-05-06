#!/usr/bin/python
# -*- coding: utf8 -*-
import re

ranges = {
    # https://en.wikipedia.org/wiki/CJK_Unified_Ideographs#CJK_Unified_Ideographs
    'CJK UI': [
        (0x4e00, 0x62ff),
        (0x6300, 0x77ff),
        (0x7800, 0x8cff),
        (0x8d00, 0x9fff)
        ],

    # https://en.wikipedia.org/wiki/CJK_Unified_Ideographs#CJK_Unified_Ideographs_Extension_A
    'CJK UI Ext A': [
        (0x3400, 0x4dbf)
        ],

    # https://en.wikipedia.org/wiki/CJK_Unified_Ideographs#CJK_Unified_Ideographs_Extension_B
    'CJK UI Ext B': [
        (0x20000, 0x215ff),
        (0x21600, 0x230ff),
        (0x23100, 0x245ff),
        (0x24600, 0x260ff),
        (0x26100, 0x275ff),
        (0x27600, 0x290ff),
        (0x29100, 0x2a6df)
        ],

    # https://en.wikipedia.org/wiki/CJK_Unified_Ideographs#CJK_Unified_Ideographs_Extension_C
    'CJK UI Ext C': [
        (0x2a700, 0x2b73f)
        ],

    # https://en.wikipedia.org/wiki/CJK_Unified_Ideographs#CJK_Unified_Ideographs_Extension_D
    'CJK UI Ext D': [
        (0x2b740, 0x2b81f)
        ],

    # https://en.wikipedia.org/wiki/Hiragana#Unicode
    'Hiragana': [
        (0x3040, 0x309f)
        ],

    # https://en.wikipedia.org/wiki/Katakana
    'Katakana': [
        (0x30a0, 0x30ff),
        (0x31f0, 0x31ff),
        (0x3200, 0x32ff),
        (0xff00, 0xffef),
        (0x1b000, 0x1b0ff)
        ],

    # https://en.wikipedia.org/wiki/CJK_Symbols_and_Punctuation
    'Symbols and Punctuation CJK': [
        (0x3000, 0x303f)
        ],

    # https://en.wikipedia.org/wiki/Halfwidth_and_fullwidth_forms
    'Halfwidth and fullwidth forms': [
        (0xff00, 0xffef)
        ],

    # https://en.wikipedia.org/wiki/ASCII
    'ASCII Alphabet': [
        (0x41, 0x5a),
        (0x61, 0x7a)
        ],
    'ASCII Numbers': [
        (0x30, 0x39)
        ],
    'ASCII Symbols': [
        (0x20, 0x2f),
        (0x3a, 0x40),
        (0x5b, 0x60),
        (0x7b, 0x7e),
        ],
}



class Classifier(object):
    @staticmethod
    def merge_ranges(range):
        _merged = []
        for i in sorted(range, key=lambda x: x[0]):
            if len(_merged):
                if _merged[-1][1]+1 >= i[0]:
                    _merged[-1] = (_merged[-1][0], max(_merged[-1][1], i[1]))
                    continue
            _merged.append(i)
        return _merged

    def __init__(self, chr_name_list):
        self._ranges = []
        for i in chr_name_list:
            self._ranges += ranges[i]

        self._ranges = Classifier.merge_ranges(self._ranges)

    def __call__(self, char):
        od = ord(char)
        for i in self._ranges:
            if od >= i[0] and od <= i[1]:
                return True

        return False

def unicode_full_width_to_half(s):
    def _one(char):
        code = ord(char)
        if code >= 0xff01 and code <= 0xff5e:
            code -= 0xff01
            code += 0x21
            return unichr(code)
        elif code == 0x3000:
            return unichr(0x20)
        else:
            return char

    return ''.join(map(_one, s))

cjk_char_name = [
    'CJK UI', 
    'CJK UI Ext A',
    'CJK UI Ext B',
    'CJK UI Ext C',
    'CJK UI Ext D']
ascii_char_name = [
    'ASCII Alphabet',
    'ASCII Numbers']
ascii_symbols_name = [
    'ASCII Symbols']
cjk_symbols_name = [
    'Symbols and Punctuation CJK']
full_width_symbols = [
    'Halfwidth and fullwidth forms']

is_cjk_char = Classifier(cjk_char_name)
is_ascii_char = Classifier(ascii_char_name)
is_oridinary_char = Classifier(cjk_char_name+ascii_char_name+cjk_symbols_name+ascii_symbols_name+full_width_symbols)

is_good_char = Classifier(cjk_char_name+[
    'ASCII Alphabet',
    'ASCII Numbers',
    ])

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print '''This script finds weird verbs from a verb list extracted from tuples.

Good verbs are considered as only contaning CJK chars, ASCII chars, numbers, 
words split by 、/ are also good verbs.'''
        sys.exit(1)

    input = sys.argv[1]

    units = re.compile(ur'^(.*?)\((.*?)\)$')
    parallel = re.compile(ur'^(.*?)[\/、](.*?)$')

    def get_group_text(regx, s):
        match = re.match(regx, s)
        if match:
            try:
                return next(item for item in match.groups() if item)
            except StopIteration as e:
                # nothing remains...
                return u''

        return s

    for l in open(input):
        line = l[:l.rfind('\t')].decode('utf8')
        line = get_group_text(units, line)
        line = get_group_text(parallel, line)

        for i in line:
            if not is_good_char(i):
                print line.encode('utf8'), l[l.rfind('\t')+1:l.rfind('\n')]
                break