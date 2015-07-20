#!/usr/bin/env python
import logging
import subprocess
import threading

import pymongo
import threadpool

if __name__  == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='parallel process mongodb baidu baike data.')
    parser.add_argument('--mongod-host', type=str, required=True, help='host of mongo db server.')
    parser.add_argument('--mongod-port', type=int, required=True, help='port of mongo db server.')
    parser.add_argument('--worker-job-count', type=int, default=100000, help='how many pages should a worker work on.')
    parser.add_argument('--worker-count', type=int, default=10, help='how many workers should be there.')

    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    def get_doc_count():
        client = pymongo.MongoClient(args.mongod_host, args.mongod_port)
        c = client.baidu.data.find().count()
        client.close()
        return c

    def process(params):
        slice_from, slice_to = params
        worker_id = str(threading.current_thread().ident)

        logging.info('worker %s started, working on doc %d-%d', worker_id, slice_from, slice_to)

        subprocess.call(['/usr/bin/env', 'python', 'manage.py', 'bdbk_extract'
                         '--src', 'mongodb',
                         '--mongod-host', args.mongod_host,
                         '--mongod-port', str(args.mongod_port),
                         '--mongod-from-to', '%d-%d' % (slice_from, slice_to)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        logging.info('worker %s paused', worker_id)

    pool = threadpool.ThreadPool(args.worker_count)

    jobs = []
    total_docs = get_doc_count()
    for i in range(0, total_docs, args.worker_job_count):
        jobs.append([i, min(i+args.worker_job_count, total_docs)])

    logging.info('%d jobs ==> %d workers', len(jobs), args.worker_count)
    reqs = threadpool.makeRequests(process, jobs)
    [pool.putRequest(req) for req in reqs]
    pool.wait()
    logging.info('all workers stopped')
