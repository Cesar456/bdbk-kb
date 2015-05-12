#!/usr/bin/python
import gzip
import os


class BaiduDatabase(object):
    def __init__(self, dir, db_name):
        self.dir = dir
        self.db_name = db_name
        self.opened_chunk = None
        self.opened_chunk_id = -1

        self.pages = []
        with open(os.path.join(dir, '%s.index' % db_name)) as idx_file:
            for i in idx_file:
                _page_id, _title, _chunk_id, _offset, _size = \
                    i.rstrip().split('\t')

                self.pages.append((int(_page_id), _title, int(_chunk_id), int(_offset), int(_size)))

    def seek_to_page(self, chunkid, offset):
        if self.opened_chunk_id != chunkid:
            if self.opened_chunk:
                self.opened_chunk.close()

            self.opened_chunk_id = chunkid
            self.opened_chunk = gzip.open(\
                os.path.join(self.dir, '%s.%.3d.gz' % (self.db_name, chunkid)))
        self.opened_chunk.seek(offset)

    def get_page(self, page_id=None, page_title=None):
        if page_id == None and page_title == None:
            raise ValueError('either page_id or page_title must not be None')

        for i in self.pages:
            if (page_id and page_id == i[0]) \
                or (page_title and page_title == i[1]):

                self.seek_to_page(i[2], i[3])
                data = self.opened_chunk.read(i[4])
                if len(data) != i[4]:
                    raise IOError('chunk %d is corrupted' % i[4])

                return data

        return None

    def close(self):
        if self.opened_chunk:
            self.opened_chunk.close()

        self.opened_chunk_id = -1

    def all_pages(self):
        for i in self.pages:
            yield (i[0], i[1], self.get_page(i[0]))

    def get_page_id_list(self):
        return [x[0] for x in self.pages]

def get_page(dir, db_name, page_id=None, page_name=None):
    db = BaiduDatabase(dir, db_name)
    data = db.get_page(page_id, page_name)
    db.close()
    return data

def get_page_id_list(dir, db_name):
    db = BaiduDatabase(dir, db_name)
    lst = db.get_page_id_list()

    return lst

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
