#!/usr/bin/python
# This script converts raw tuples into sql inserts, 
# using django's powerful ORM framework

import sys
import pickle
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
        description='Convert raw tuples into sql inserts')
    parser.add_argument('--tuple-type', required=True, help='baidu,zhwiki')
    parser.add_argument('--tuple-file', required=True, help='tuple file of baike data.')
    parser.add_argument('--ne-dict', help='named entity dict file, used when recovering from a previous state.')
    parser.add_argument('--vb-dict', help='verb dict file, used when recovering from a previous state.')
    parser.add_argument('--skip-lines', type=int, help='skip first N lines, aka recover from a previous state.')
    parser.add_argument('--error-log', required=True, help='error log file')

    args = parser.parse_args()
    tuple_type = args.tuple_type
    tuple_fn = args.tuple_file
    skip_lines = args.skip_lines
    log_fn = args.error_log

    # check arguments
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

    if tuple_type != 'baidu' and tuple_type != 'zhwiki':
        print '--tuple-type must be baidu or zhwiki'
        sys.exit(1)

    # init dict and log file
    ne_dict = NamedEntityDict(ne_dict_fn)
    vb_dict = VerbDict(vb_dict_fn)
    problems = open(log_fn, 'a')
    print 'Output problems into', log_fn

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

    def process_line_baidu(line):
        ne, verb, target = line.rstrip().split('\t')
        if ne not in ne_dict:
            n = BaiduNamedEntity(name=ne)
            n.save()
            ne_dict[ne] = n.pk

        if verb not in vb_dict:
            v = BaiduVerb(name=verb)
            v.save()
            vb_dict[verb] = v.pk

        r = BaiduRelation(content=target,
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
                if tuple_type == 'baidu':
                    process_line_baidu(line.decode('utf8'))
                else:
                    process_line_zhwiki(line.decode('utf8'))
            except Exception as e:
                print 'ERROR', e
                #print 'Saving state...'
                #print 'Dumping Dicts...'
                #ne_dict.save_state('saved_ne_dict.pickle')
                #vb_dict.save_state('saved_vb_dict.pickle')
                #print 'Saved to saved_ne_dict.pickle and saved_vb_dict.pickle'
                problems.write('Problem encountered when processing line #%d, %r\n' % (line_counter, e))

    problems.close()
