#!/usr/bin/python
# This script converts raw tuples into sql inserts, 
# using django's powerful ORM framework

import sys
import pickle
from setup_database import Verb, NamedEntity, Relation

class NamedEntityDict(object):
    def __init__(self, dict_fn=None):
        if dict_fn:
            f = open(dict_fn, 'rb')
            d = pickle.load(f)
            f.close()

            self._dict = d
        else:
            self._dict = {}

    def __contains__(self, name):
        return self._dict.__contains__(name)

    def __setitem__(self, name, val):
        return self._dict.__setitem__(name, val)

    def __getitem__(self, name):
        return self._dict.__getitem__(name)

    def save_state(self, fn):
        f = open(fn, 'wb')
        pickle.dump(self._dict, f)
        f.close()

class VerbDict(NamedEntityDict):
    pass

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Convert raw tuples into sql inserts')
    parser.add_argument('--tuple-file', required=True, help='tuple file of baike data.')
    parser.add_argument('--ne-dict', help='named entity dict file, used when recovering from a previous state.')
    parser.add_argument('--vb-dict', help='verb dict file, used when recovering from a previous state.')
    parser.add_argument('--skip-lines', type=int, help='skip first N lines, aka recover from a previous state.')

    args = parser.parse_args()
    tuple_fn = args.tuple_file
    skip_lines = args.skip_lines

    if skip_lines:
        ne_dict_fn = args.ne_dict
        vb_dict_fn = args.vb_dict
        if not ne_dict_fn:
            print 'Named Entity Dict must be specified when recovering from a previous state.'
            sys.exit(1)
        if not vb_dict_fn:
            print 'Verb Dict must be specified when recovering from a previous state.'
            sys.exit(1)
    else:
        ne_dict_fn = None
        vb_dict_fn = None

    ne_dict = NamedEntityDict(ne_dict_fn)
    vb_dict = VerbDict(vb_dict_fn)
    problems = open('problems.log', 'wa')
    print 'Output problems into problems.log'

    def convert_line(line):
        ne, verb, target = line.rstrip().split('\t')
        if ne not in ne_dict:
            n = NamedEntity(name=ne)
            n.save()
            ne_dict[ne] = n.pk

        if verb not in vb_dict:
            v = Verb(name=verb)
            v.save()
            vb_dict[verb] = v.pk

        r = Relation(content=target,
                named_entity_id=ne_dict[ne],
                verb_id=vb_dict[verb])
        r.save()

    with open(tuple_fn, 'r') as tuple_file:

        line_counter = 0

        for line in tuple_file:
            line_counter += 1
            if line_counter % 1000 == 0:
                print line_counter, 'processed'

            if skip_lines:
                skip_lines -= 1
                continue

            try:
                convert_line(line.decode('utf8'))
            except Exception as e:
                print 'ERROR', e
                #print 'Saving state...'
                #print 'Dumping Dicts...'
                #ne_dict.save_state('saved_ne_dict.pickle')
                #vb_dict.save_state('saved_vb_dict.pickle')
                #print 'Saved to saved_ne_dict.pickle and saved_vb_dict.pickle'
                problems.write('Problem encountered when processing line #%d, %r' % line_counter, e)

    problems.close()
