#!/usr/bin/python

import os
import random
from baidu_database import *

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Select random pages from baidu baike database.')
    parser.add_argument('--dir', required=True, help='databases base directory.')
    parser.add_argument('--output-dir', required=True, help='output dir.')

    args = parser.parse_args()
    dir = args.dir
    output_dir = args.output_dir

    for i in os.listdir(dir):
        path = os.path.join(dir, i)
        lst = get_page_id_list(path, 'baike_data')
        random.shuffle(lst)
        lst = lst[:20]
        
        for j in lst:
            page = get_page(path, 'baike_data', j)

            with open(os.path.join(output_dir, '%.8d.html' % j), 'w') as f:
                f.write(page)
