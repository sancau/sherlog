# TODO allow multiprocessing via 1 worker instance like: sherlog worker -c config.yaml -max 10
# TODO push event back to queue if insert failed? Need to?
# TODO logging for sherlog itself

# coding=utf-8

import json
import traceback

from redis import StrictRedis

from sherlog.postgresql import PostgresqlBackend


class SherlogWorker(object):
    """A Redis => DB worker"""

    def __init__(self, backend, config, blocking_timeout=1):
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
                event = json.loads(str(data[1]).encode('utf-8'))
                self.backend.insert_event(event)
            except Exception as e:
                print(e, traceback.format_exc())  # TODO logging
