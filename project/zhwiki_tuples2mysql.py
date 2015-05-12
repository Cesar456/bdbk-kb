#!/usr/bin/python
# This script converts raw tuples into sql inserts, 
# using django's powerful ORM framework

import pickle
import sys

from project.setup_database import *


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
        description='Convert raw tuples from zhwiki into sql inserts')
    parser.add_argument('--tuple-file', required=True, help='tuple file of zhwiki data.')
    parser.add_argument('--error-log', required=True, help='error log file')

    args = parser.parse_args()
    tuple_fn = args.tuple_file
    log_fn = args.error_log

    # init dict and log file
    ne_dict = NamedEntityDict()
    vb_dict = VerbDict()
    from project.setup_logging import setup as setup_log
    logging = setup_log(log_fn)
    logging.info('Output problems into %s', log_fn)

    def process_line_zhwiki(line):
        neid, vid, targetid, ne, verb, target = line.rstrip().split('\t')
        if ne not in ne_dict:
            n = ZhWikiNamedEntity(name=ne, neid=int(neid))
            n.save()
            ne_dict[ne] = n.pk

        if verb not in vb_dict:
            v = ZhWikiVerb(name=verb)
            v.save()
            vb_dict[verb] = v.pk

        r = ZhWikiRelation(content=target,
                named_entity_id=ne_dict[ne],
                verb_id=vb_dict[verb])

        if int(targetid) != 0:
            r.content_neid = int(targetid)

        r.save()

    with open(tuple_fn, 'r') as tuple_file:

        line_counter = 0

        for line in tuple_file:
            line_counter += 1
            if line_counter % 1000 == 0:
                logging.info('%d processed', line_counter)

            try:
                process_line_zhwiki(line.decode('utf8'))
            except Exception as e:
                logging.error('Problem encountered when processing line #%d, %r', line_counter, e)
