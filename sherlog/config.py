# coding=utf-8

import json
import yaml

from io import open

from collections import namedtuple


SherlogPostgresqlConfig = namedtuple('SherlogPostgresqlConfig',
                                     ['host', 'port', 'database',
                                      'user', 'password',
                                      'schema', 'table'])

SherlogRedisConfig = namedtuple('SherlogRedisConfig', ['host', 'port', 'key'])


SherlogMonitorFilterConfig = namedtuple('SherlogMonitorFilterConfig', ['apps', 'fields',
                                                                       'levels', 'loggers'])


class SherlogConfig(object):
    """Base class for Sherlog configuration"""

    def __init__(self, dict_config):
        self.validate(dict_config)

    @staticmethod
    def validate(dict_config):
        raise NotImplementedError

    @staticmethod
    def sql_user_input_safe(s):  # TODO more robust sanitation
        return len(s.split(' ')) == 1 and ';' not in s and s.lower() not in ['drop', 'insert',
                                                                             'update', 'create']

    @classmethod
    def from_json(cls, filepath, encoding='UTF8'):
        with open(filepath, encoding=encoding) as f:
            dict_config = json.loads(f.read())
        return cls(dict_config=dict_config)

    @classmethod
    def from_yaml(cls, filepath, encoding='UTF8'):
        with open(filepath, encoding=encoding) as f:
            dict_config = yaml.load(f.read())
        return cls(dict_config=dict_config)


class SherlogClientConfig(SherlogConfig):
    """Configuration to initialize python logger"""

    def __init__(self, dict_config):
        super(SherlogClientConfig, self).__init__(dict_config)

        self.redis = SherlogRedisConfig(dict_config['redis']['host'],
                                        dict_config['redis']['port'],
                                        dict_config['redis']['key'])

        self.app = dict_config['app']
        self.level = dict_config['level']
        self.stdout = dict_config['stdout']

    @staticmethod
    def validate(dict_config):
        return True  # TODO validation using Validoll


class SherlogBackendConfig(SherlogConfig):
    """Configuration for Sherlog worker"""

    def __init__(self, dict_config):
        super(SherlogBackendConfig, self).__init__(dict_config)

        self.redis = SherlogRedisConfig(dict_config['redis']['host'],
                                        dict_config['redis']['port'],
                                        dict_config['redis']['key'])

        self.postgresql = SherlogPostgresqlConfig(dict_config['postgresql']['host'],
                                                  dict_config['postgresql']['port'],
                                                  dict_config['postgresql']['database'],
                                                  dict_config['postgresql']['user'],
                                                  dict_config['postgresql']['password'],
                                                  dict_config['postgresql']['schema'],
                                                  dict_config['postgresql']['table'])

    @staticmethod
    def validate(dict_config):
        if 'postgresql' not in dict_config:
            raise ValueError('PostgreSQL config required.')

        psql = dict_config['postgresql']

        if not all(['schema' in psql, 'table' in psql]):
            raise ValueError('PostgreSQL schema and table required.')

        if not SherlogConfig.sql_user_input_safe(psql['schema']):
            raise ValueError('Unsafe PSQL schema name provided.')

        if not SherlogConfig.sql_user_input_safe(psql['table']):
            raise ValueError('Unsafe PSQL table name provided.')


class SherlogMonitorConfig(SherlogConfig):
    """Configuration for Sherlog monitor"""

    def __init__(self, dict_config):
        super(SherlogMonitorConfig, self).__init__(dict_config)

        self.postgresql = SherlogPostgresqlConfig(dict_config['postgresql']['host'],
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
            levels = filters.get('levels', None)
            loggers = filters.get('loggers', None)

            self.filters = SherlogMonitorFilterConfig(apps, fields, levels, loggers)
        else:
            self.filters = SherlogMonitorFilterConfig(None, None, None, None)

    @staticmethod
    def validate(dict_config):
        if 'postgresql' not in dict_config:
            raise ValueError('PostgreSQL config required.')

        psql = dict_config['postgresql']

        if not all(['schema' in psql, 'table' in psql]):
            raise ValueError('PostgreSQL schema and table required.')

        if not SherlogConfig.sql_user_input_safe(psql['schema']):
            raise ValueError('Unsafe PSQL schema name provided.')

        if not SherlogConfig.sql_user_input_safe(psql['table']):
            raise ValueError('Unsafe PSQL table name provided.')
