# coding=utf-8

import json
import psycopg2

from sherlog.config import SherlogBackendConfig


class PostgresqlBackend:
    def __init__(self, config: SherlogBackendConfig):
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
            ts                 TIMESTAMP NOT NULL,
            ts_rel             INTEGER DEFAULT NULL,
            lvl                TEXT NOT NULL,
            message            TEXT DEFAULT NULL,
            module             TEXT DEFAULT NULL,
            function           TEXT DEFAULT NULL,
            line               INTEGER DEFAULT NULL,
            path               TEXT DEFAULT NULL,
            file               TEXT DEFAULT NULL,
            pid                BIGINT DEFAULT NULL,
            pname              TEXT DEFAULT NULL,
            tid                BIGINT DEFAULT NULL,
            tname              TEXT DEFAULT NULL,
            logger             TEXT DEFAULT NULL,
            ex_type            TEXT DEFAULT NULL,
            ex_repr            TEXT DEFAULT NULL,
            stack              TEXT DEFAULT NULL
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
        self.cursor.execute("""
        INSERT INTO {}.{}
            (
             app, ts, ts_rel,
             lvl, message, module, function,
             line, path, file, pid, pname,
             tid, tname, logger, ex_type, ex_repr, stack
            )
        VALUES
            (
             %(app)s, %(ts)s, %(ts_rel)s,
             %(lvl)s, %(message)s, %(module)s, %(function)s,
             %(line)s, %(path)s, %(file)s, %(pid)s, %(pname)s,
             %(tid)s, %(tname)s, %(logger)s, %(ex_type)s, %(ex_repr)s, %(stack)s
            )
        """.format(self.schema, self.table), event)
