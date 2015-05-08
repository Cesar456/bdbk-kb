#!/usr/bin/python
import os
import gzip

def get_page_id_list(dir, db_name):
    lst = []
    with open(os.path.join(dir, '%s.index' % db_name)) as idx_file:
        for i in idx_file:
            _page_id, _title, _chunk_id, _offset, _size = \
                i.rstrip().split('\t')

            lst.append(int(_page_id))

    return lst

def get_page(dir, db_name, page_id=None, page_name=None):
    if not page_id and not page_name:
        raise ValueError('either page_id or page_name must not be None')

    with open(os.path.join(dir, '%s.index' % db_name)) as idx_file:
        for i in idx_file:
            _page_id, _title, _chunk_id, _offset, _size = \
                i.rstrip().split('\t')

            if page_id and page_id == int(_page_id)\
                or page_name and page_name == _title:
                with gzip.open(os.path.join(dir, '%s.%.3d.gz' % (db_name, int(_chunk_id)))) as chunk:
                    chunk.seek(int(_offset))
                    data = chunk.read(int(_size))

                    if len(data) != int(_size):
                        raise IOError('chunk %d is corrupted' % int(_chunk_id))

                    return data

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Read a certain page from baidu baike database.')
    parser.add_argument('--dir', required=True, help='database directory.')
    parser.add_argument('--db-name', required=True, help='database name.')
    parser.add_argument('--page-id', type=int, help='a page id to be extracted.')
    parser.add_argument('--page-title', help='a page title to be extracted.')

    args = parser.parse_args()
    dir = args.dir
    db_name = args.db_name
    page_id = args.page_id
    page_title = args.page_title

    print get_page(dir, db_name, page_id, page_title).decode('utf8')