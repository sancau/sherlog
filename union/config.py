# coding=utf-8

import json
import yaml

from collections import namedtuple


UnionPostgresqlConfig = namedtuple('UnionPostgresqlConfig',
                                      ['host', 'port', 'database',
                                       'user', 'password',
                                       'schema', 'table'])

UnionRedisConfig = namedtuple('UnionRedisConfig', ['host', 'port', 'key'])


UnionMonitorFilterConfig = namedtuple('UnionMonitorFilterConfig', ['apps', 'fields',
                                                                         'types', 'loggers'])


class UnionConfig:
    """Base class for Union configuration"""

    def __init__(self, dict_config: dict):
        self.validate(dict_config)

    @staticmethod
    def validate(dict_config: dict):
        raise NotImplementedError

    @staticmethod
    def sql_user_input_safe(s):  # TODO more robust validation
        return len(s.split(' ')) == 1 and ';' not in s and s.lower() not in ['drop', 'insert',
                                                                             'update', 'create']

    @classmethod
    def from_json(cls, filepath: str, encoding='UTF8'):
        with open(filepath, encoding=encoding) as f:
            dict_config = json.loads(f.read())
        return cls(dict_config=dict_config)

    @classmethod
    def from_yaml(cls, filepath: str, encoding='UTF8'):
        with open(filepath, encoding=encoding) as f:
            dict_config = yaml.load(f.read())
        return cls(dict_config=dict_config)


class UnionClientConfig(UnionConfig):
    """Configuration to initialize python logger"""

    def __init__(self, dict_config: dict):
        super(UnionClientConfig, self).__init__(dict_config)

        self.redis = UnionRedisConfig(dict_config['redis']['host'],
                                         dict_config['redis']['port'],
                                         dict_config['redis']['key'])

        self.app = dict_config['app']
        self.level = dict_config['level']
        self.stdout = dict_config['stdout']

    @staticmethod
    def validate(dict_config: dict):
        return True  # TODO validation using Validoll


class UnionBackendConfig(UnionConfig):
    """Configuration for Union worker"""

    def __init__(self, dict_config: dict):
        super(UnionBackendConfig, self).__init__(dict_config)

        self.redis = UnionRedisConfig(dict_config['redis']['host'],
                                         dict_config['redis']['port'],
                                         dict_config['redis']['key'])

        self.postgresql = UnionPostgresqlConfig(dict_config['postgresql']['host'],
                                                   dict_config['postgresql']['port'],
                                                   dict_config['postgresql']['database'],
                                                   dict_config['postgresql']['user'],
                                                   dict_config['postgresql']['password'],
                                                   dict_config['postgresql']['schema'],
                                                   dict_config['postgresql']['table'])

    @staticmethod
    def validate(dict_config: dict):
        if 'postgresql' not in dict_config:
            raise ValueError('PostgreSQL config required.')

        psql = dict_config['postgresql']

        if not all(['schema' in psql, 'table' in psql]):
            raise ValueError('PostgreSQL schema and table required.')

        if not UnionConfig.sql_user_input_safe(psql['schema']):
            raise ValueError('Unsafe PSQL schema name provided.')

        if not UnionConfig.sql_user_input_safe(psql['table']):
            raise ValueError('Unsafe PSQL table name provided.')


class UnionMonitorConfig(UnionConfig):
    """Configuration for Union monitor"""

    def __init__(self, dict_config: dict):
        super(UnionMonitorConfig, self).__init__(dict_config)

        self.postgresql = UnionPostgresqlConfig(dict_config['postgresql']['host'],
                                                   dict_config['postgresql']['port'],
                                                   dict_config['postgresql']['database'],
                                                   dict_config['postgresql']['user'],
                                                   dict_config['postgresql']['password'],
                                                   dict_config['postgresql']['schema'],
                                                   dict_config['postgresql']['table'])

        filters = dict_config.get('filters', None)
        if filters:
            apps = filters.get('apps', None)
            fields = filters.get('fields', None)
            types = filters.get('types', None)
            loggers = filters.get('loggers', None)

            self.filters = UnionMonitorFilterConfig(apps, fields, types, loggers)
        else:
            self.filters = UnionMonitorFilterConfig(None, None, None, None)

    @staticmethod
    def validate(dict_config: dict):
        if 'postgresql' not in dict_config:
            raise ValueError('PostgreSQL config required.')

        psql = dict_config['postgresql']

        if not all(['schema' in psql, 'table' in psql]):
            raise ValueError('PostgreSQL schema and table required.')

        if not UnionConfig.sql_user_input_safe(psql['schema']):
            raise ValueError('Unsafe PSQL schema name provided.')

        if not UnionConfig.sql_user_input_safe(psql['table']):
            raise ValueError('Unsafe PSQL table name provided.')
