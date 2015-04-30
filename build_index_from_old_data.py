import os
import gzip
import sys
import logging

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

def process_folder(folder):
    # the folder contains %.4d/pid_ptitle
    for subfolder in os.listdir(folder):
        for fn in os.listdir(os.path.join(folder, subfolder)):

            path = os.path.join(folder, subfolder, fn)
            try:
                f = open(path)
                page_id, page_title = fn.split('_', 1)
                page_id = int(page_id)
                content = f.read()
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

subfolders = os.listdir(source_folder)
for subfolder in subfolders:
    if 'other' not in subfolder:
        process_folder(os.path.join(source_folder, subfolder))

blocks.close()