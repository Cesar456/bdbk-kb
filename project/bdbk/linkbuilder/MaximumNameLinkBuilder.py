# -*- coding: utf-8 -*-
import os
import subprocess
from bdbk.models import NamedEntity, NamedEntityAlias

from .LinkBuilder import LinkBuilder


class MaximumNameLinkBuilder(LinkBuilder):
    '''
    寻找最长公共子串.
    效果很差！
    '''
    def find_links(self):
        pipe = subprocess.Popen(os.path.dirname(__file__) + '/max_common_string_in_set',
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                bufsize=0)

        # FIXME: newline char replace?
        for i in self.iterator(NamedEntityAlias):
            pipe.stdin.write(i.link_from.upper().encode('utf8'))
            pipe.stdin.write('\t')
            pipe.stdin.write('alias_id:%d\n' % i.pk)
        for i in self.iterator(NamedEntity):
            pipe.stdin.write(i.name.upper().encode('utf8'))
            pipe.stdin.write('\t')
            pipe.stdin.write('ne_name\n')
            pipe.stdin.write(i.search_term.upper().encode('utf8'))
            pipe.stdin.write('\t')
            pipe.stdin.write('ne_st\n')

        pipe.stdin.write('\n')
        pipe.stdin.flush()

        for tuple in self.infobox_iterator():
            new_links = []
            existing_links, content = self.strip_links(tuple.content)

            if not content:
                continue

            # newline char will mess up everything
            pipe.stdin.write(content.replace('\n', '.').upper().encode('utf8'))
            pipe.stdin.write('\n')
            pos = 0
            while True:
                line = pipe.stdout.readline()
                line = line.strip('\n').decode('utf8')
                if not line:
                    break

                if '\t' in line:
                    end_pos = pos + len(line.split('\t')[0])
                    for obj, is_ne_or_alias in self.resolve_name(content[pos:end_pos]):
                        new_links.append({
                            'start': pos,
                            'end': end_pos,
                            'link_type': 'ne_id' if is_ne_or_alias else 'alias_id',
                            'link_to': obj.pk
                        })
                else:
                    end_pos = pos + len(line)

                pos = end_pos

            if len(new_links):
                print 'Found new links for tuple (%s,%s,%s)' % (tuple.named_entity.name, tuple.verb.name, tuple.content),\
                    new_links, existing_links
