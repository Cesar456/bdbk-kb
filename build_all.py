# a script which lists all the old tar-ed baike database and starts another python 
# instance, and converts all the data.
import os
import subprocess
import re

mch = re.compile(r'File(\d+)~(\d+).tar.gz')
src_folder = "F:/laiyuxuan/baidudownload/"
dst_folder = "F:/huohaoyan/"

for fn in os.listdir(src_folder):
	if 'File' not in fn:
		continue
	
	mh = re.match(mch, fn)
	if not mh:
		continue
	
	start_id = int(mh.group(1))
	end_id = int(mh.group(2))
	extract_folder = os.path.join(dst_folder, '%d-%d' % (start_id, end_id))
	os.mkdir(extract_folder)
	
	subprocess.call([
		'C:/python27/python.exe', 
		'build_index_win_server.py',
		os.path.join(src_folder, fn),
		extract_folder,
		os.path.join(extract_folder, 'build.log')
		])
	