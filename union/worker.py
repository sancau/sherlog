# TODO allow multiprocessing via 1 worker instance like: union worker -c config.yaml -max 10
# TODO push event back to queue if insert failed? Need to?
# TODO logging for union itself

# coding=utf-8

import json

from redis import StrictRedis

from union.config import UnionBackendConfig
from union.postgresql import PostgresqlBackend


class UnionWorker:
    """A Redis => DB worker"""

    def __init__(self, *, backend, config: UnionBackendConfig, blocking_timeout=1):
        backend_map = {
            'psql': PostgresqlBackend,
        }

        self.backend = backend_map.get(backend, None)(config=config)
        if not self.backend:
            raise ValueError('Requested backend ({}) is not supported.'.format(backend))

        host, port = config.redis.host, config.redis.port

        self.blocking_timeout = blocking_timeout
        self.redis_key = config.redis.key
        self.redis = StrictRedis(host=host, port=port)

    def work(self):
        data = self.redis.brpop(self.redis_key, self.blocking_timeout)
        if data:
            try:
                event = json.loads(str(data[1], encoding='UTF8'))
                self.backend.insert_event(event)
            except Exception as e:
                print(e)  # TODO
