# coding=utf-8

import json
import psycopg2

from union.config import UnionBackendConfig


class PostgresqlBackend:
    def __init__(self, config: UnionBackendConfig):
        conn = psycopg2.connect(host=config.postgresql.host,
                                port=config.postgresql.port,
                                database=config.postgresql.database,
                                user=config.postgresql.user,
                                password=config.postgresql.password)

        conn.autocommit = True

        self.cursor = conn.cursor()
        self.schema = config.postgresql.schema  # already sanitized
        self.table = config.postgresql.table  # already sanitized
        self.prepare_db()

    @property
    def create_table_query(self):
        return """
        CREATE TABLE {}.{} (
            id                 SERIAL NOT NULL PRIMARY KEY,
            app                TEXT NOT NULL,
            timestamp          TIMESTAMP NOT NULL,
            timestamp_relative NUMERIC DEFAULT NULL,
            type               TEXT NOT NULL,
            message            TEXT DEFAULT NULL,
            module             TEXT DEFAULT NULL,
            function           TEXT DEFAULT NULL,
            line               NUMERIC DEFAULT NULL,
            path               TEXT DEFAULT NULL,
            filename           TEXT DEFAULT NULL,
            process_id         INTEGER DEFAULT NULL,
            process_name       TEXT DEFAULT NULL,
            thread_id          NUMERIC DEFAULT NULL,
            thread_name        TEXT DEFAULT NULL,
            logger             TEXT DEFAULT NULL,
            exception          JSON DEFAULT NULL,
            stacktrace         JSON DEFAULT NULL
        );""".format(self.schema, self.table)

    @property
    def create_schema_query(self):
        return """
        create schema {};
        """.format(self.schema)

    @property
    def create_trigger_query(self):  # drop statement adds create or replace behavior
        return """
        drop trigger if exists {schema}_{table}_notify_trigger on {schema}.{table};
        create trigger {schema}_{table}_notify_trigger after insert or update on {schema}.{table}
            for each row execute procedure {schema}_{table}_notify_func();
        """.format(schema=self.schema, table=self.table)

    @property
    def create_function_query(self):
        return """
        create or replace function {schema}_{table}_notify_func() returns trigger as $$
            begin
                perform pg_notify(CAST('{schema}_{table}_updates' as text), row_to_json(new)::text);
                return new;
            end;
        $$ language plpgsql;""".format(schema=self.schema, table=self.table)

    def ensure_table_structure(self):
        self.cursor.execute("""
        select column_name, data_type
            from information_schema.columns 
        where table_schema = %s and table_name = %s;""", (self.schema, self.table))

        # TODO then check if structure is OK if not raise
        table_info = self.cursor.fetchall()

    def create_schema(self):
        self.cursor.execute("""
        select exists(
            select schema_name 
            from information_schema.schemata 
            where schema_name = '{}'
        );""".format(self.schema))

        schema_exists = self.cursor.fetchone()[0]

        if not schema_exists:
            self.cursor.execute(self.create_schema_query)       

    def create_table(self):
        self.cursor.execute("""
        select exists (
           select 1
           from   information_schema.tables
           where  table_schema = '{}'
           and    table_name = '{}'
        );""".format(self.schema, self.table))

        table_exists = self.cursor.fetchone()[0]

        if not table_exists:
            self.cursor.execute(self.create_table_query)
        else:
            self.ensure_table_structure()

    def prepare_db(self):
        self.create_schema()
        self.create_table()
        self.cursor.execute(self.create_function_query)
        self.cursor.execute(self.create_trigger_query)

    def insert_event(self, event):
        event['exception'] = json.dumps(event['exception'])
        event['stacktrace'] = json.dumps(event['stacktrace'])

        self.cursor.execute("""
        INSERT INTO {}.{}
            (
             app, timestamp, timestamp_relative,
             type, message, module, function,
             line, path, filename, process_id, process_name,
             thread_id, thread_name, logger, exception, stacktrace
            )
        VALUES
            (
             %(app)s, %(timestamp)s, %(timestamp_relative)s,
             %(type)s, %(message)s, %(module)s, %(function)s,
             %(line)s, %(path)s, %(filename)s, %(process_id)s, %(process_name)s,
             %(thread_id)s, %(thread_name)s, %(logger)s, %(exception)s, %(stacktrace)s
            )
        """.format(self.schema, self.table), event)
