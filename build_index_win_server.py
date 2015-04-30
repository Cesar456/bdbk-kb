# this script builds the standard baike database from old tar-ed baike database
# every "standard baike database" has a index file, from which we could read the pointer of baike pages.
# page strings are stored in a very compact format(side by side).
# every line in index file has the format of:
# 			page_id(in baidu_baike's url-schema) page_title gziped_file_id offset_in_file size_of_page
# note that offset_in_file should be interpreted as the offset in pure-text file, that is, when the gzip
# file is decompressed. all pages are stored in UTF8 encoding, which is the standard of baidu baike HTTP
# server.
import os
import gzip
import sys
import re
import logging
import tarfile

source_folder = sys.argv[1]
dest_folder = sys.argv[2]
log_fn = sys.argv[3]

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-4.4s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler(log_fn)
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.WARNING)
rootLogger.addHandler(consoleHandler)

logging.info('Source folder: %s', source_folder)
logging.info('Destination folder: %s', dest_folder)

class Database(object):
    ESTIMATED_LENGTH = 1024 * 1024 * 100

    def _close_file(self):
        self.opened_file.close()

    def _open_file(self):
        self.opened_name = '%s.%.3d.gz' % (self.name, self.fileid)
        self.opened_file = gzip.open(self.opened_name, 'w')
        self.file_length = 0

    def __init__(self, name='baike_data'):
        self.name = name
        self.fileid = 0
        self._open_file()
        self.index_file = open('%s.index' % self.name, 'w')

    def put_page(self, page_id, page_title, page_text):
        try:
            if type(page_text) == unicode:
                page_text = page_text.encode('utf8')
            if type(page_title) == unicode:
                page_title = page_title.encode('utf8')

            length = len(page_text)
            self.index_file.write('%d\t%s\t%d\t%d\t%d\n' % (page_id, page_title, self.fileid, self.file_length, length))
            self.opened_file.write(page_text)
            self.file_length += length

            if self.file_length >= self.ESTIMATED_LENGTH:
                self._close_file()
                self.fileid += 1
                self._open_file()
        except KeyboardInterrupt as e:
            self.close()
            raise e

    def close(self):
        self._close_file()
        self.index_file.close()

blocks = Database(dest_folder + '/baike_data')

def process_file(fo, page_id, page_title, path):
    try:
        content = fo.read()
        try:
            content_decoded = content[:len(content) / 10].decode('utf8')
            blocks.put_page(page_id, page_title, content)
            logging.info('Processed: %s', path)
        except UnicodeError as e:
            logging.info('UnicodeError: %s', path)
    except ValueError as e:
        logging.warning('Bad filename: %s', path)
    except Exception as e:
        logging.error('Could not process(%r): %s', e, path)

mch = re.compile(r'left/\d+/(\d+)_(.*?)\.html')

tarf = tarfile.open(source_folder)
print 'Processing', source_folder
tfn = tarf.next()
processed = 0
while tfn:
    path = tfn.path.decode('utf8')
    mh = re.match(mch, path)
    if not mh:
        logging.warning('Unsupported path: %s', path)
    else:
        tf = tarf.extractfile(tfn)
        process_file(tf, int(mh.group(1)), mh.group(2), path)

	if processed % 1000 == 0:
		print 'Processed', processed, 'pages'
		
	processed += 1
    tfn = tarf.next()
    
blocks.close()