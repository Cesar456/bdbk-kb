#!/usr/bin/python

from process_relations import *
import sys

if __name__ == '__main__':
    tuple_file = sys.argv[1]
    output_file = sys.argv[2]

    print 'Dumping', tuple_file, 'to', output_file

    f = open(tuple_file)
    o = open(output_file, 'w')
    for i in f:
        subject, verb, target = i.rstrip().split('\t')
        verb = cleanup_verb(verb.decode('utf8')).encode('utf8')

        if not verb:
            continue

        o.write(subject)
        o.write('\t')
        o.write(verb)
        o.write('\t')
        o.write(target)
        o.write('\n')

    f.close()
    o.close()