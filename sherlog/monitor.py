# coding=utf-8

"""Sherlog monitor CLI script. Using PostgreSQL pubsub"""

import json
import select
import psycopg2

from sherlog.config import SherlogMonitorConfig


class SherlogMonitor:
    def __init__(self, *, config: SherlogMonitorConfig):
        self.config = config

    def listen(self):
        conn = psycopg2.connect(host=self.config.postgresql.host,
                                port=self.config.postgresql.port,
                                database=self.config.postgresql.database,
                                user=self.config.postgresql.user,
                                password=self.config.postgresql.password)

        conn.autocommit = True

        cursor = conn.cursor()
        cursor.execute(
            'LISTEN {schema}_{table}_updates;'.format(schema=self.config.postgresql.schema,
                                                      table=self.config.postgresql.table))

        while True:
            if select.select([conn], [], [], 5) != ([], [], []):
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    event = json.loads(notify.payload)
                    yield event
