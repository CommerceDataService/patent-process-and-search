import hashlib
import os

WORKER_ID_VAR = 'GO_JOB_RUN_INDEX'
WORKER_COUNT_VAR = 'GO_JOB_RUN_COUNT'


class Partitioner(object):
    def __init__(self, source, worker_id=None, n_workers=None):

        if worker_id is None and WORKER_ID_VAR in os.environ:
            worker_id = int(os.environ.get(WORKER_ID_VAR))

        if n_workers is None and WORKER_COUNT_VAR in os.environ:
            n_workers = int(os.environ.get(WORKER_COUNT_VAR))


        if worker_id == 0:
            raise RuntimeError("Worker id cannot be 0")

        if worker_id > n_workers:
            raise RuntimeError("Worker id cannot exceed number of workers")

        self.n = n_workers
        self.k = worker_id
        self.source = source

    def is_mine(self, obj_id):

        part = (obj_id % self.n)
        return part == (self.k - 1)

    def get_obj_id(self, obj):

        d = hashlib.md5(obj.encode('utf-8')).digest()
        return d[0]

    def get_my_stream(self):

        for x in self.source:
            id = self.get_obj_id(x)
            if self.is_mine(id):
                yield x
