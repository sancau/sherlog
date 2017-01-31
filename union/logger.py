# coding=utf-8

import json
import logging
import os
import sys

from datetime import datetime

from logging import Handler
from logging import Formatter

from redis import StrictRedis

from union.config import UnionClientConfig


__author__ = 'github.com/sancau'


LVL_MAP = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}


class RedisHandler(Handler):
    """Handler meant to use REDIS lpush rpop pattern
    """
    def __init__(self, redis: StrictRedis, key: str):
        self.redis = redis
        self.key = key
        super(RedisHandler, self).__init__()

    def emit(self, record):
        try:
            log_entry = self.format(record)
            json_entry = json.dumps(log_entry)
            self.redis.lpush(self.key, json_entry)
        except Exception as e:
            print(e)  # TODO logging


class UnionFormatter(Formatter):
    """Union union formatter. Performs log event pre processing.
    """
    def __init__(self, *, app: str, format_style='%'):
        supported_styles = ['%', ]
        if format_style not in supported_styles:
            raise ValueError('Given format style is not supported.')

        self.app = app
        self.format_style = format_style

        super(UnionFormatter, self).__init__()

    def format_message(self, record):
        if self.format_style == '%':
            return str(record.msg) % record.args
        else:
            raise NotImplementedError('Unexpected formatting style.')

    def format(self, record):
        ts = datetime.fromtimestamp(record.created).isoformat()

        data = {
            'type': record.levelname.lower(),
            'timestamp': ts,
            'timestamp_relative': round(record.relativeCreated / 1000, 3),  # seconds
            'app': self.app,
            'process_id': record.process,
            'process_name': record.processName,
            'thread_id': record.thread,
            'thread_name': record.threadName,
            'filename': record.filename,
            'path': record.pathname,
            'module': record.module,
            'logger': record.name,
            'function': record.funcName,
            'line': record.lineno,
            'message': self.format_message(record),
            'exception': None,
            'stacktrace': None
        }

        if record.exc_info:
            data['exception'] = {
                'type': record.exc_info[0].__name__,  # type of exception (class name)
                'repr': self.formatException(record.exc_info)
            }
        if record.stack_info:
            data['stacktrace'] = {
                'repr': self.formatStack(record.stack_info)
            }

        return data


def set_logger(name=None, *, config, format_style='%', extra_handlers=None):  # TODO more f. styles
    """Initializes union logger configuration"""
    logger = logging.getLogger(name)

    if [h for h in logger.handlers if type(h) == RedisHandler]:
        raise ValueError('Logger with name {} is already initialized by Union.'.format(name))

    if isinstance(config, dict):
        config = UnionClientConfig(dict_config=config)
    elif isinstance(config, str):
        ext = os.path.splitext(config)[1]
        if ext.lower() == '.yaml':
            config = UnionClientConfig.from_yaml(config)
        elif ext.lower() == '.json':
            config = UnionClientConfig.from_json(config)
        else:
            raise ValueError('Unsupported config file extension: {}'.format(ext))
    else:
        raise ValueError('Union config should be either Python Dict, .yaml file or .json file')

    app = config.app

    logger_level = LVL_MAP[config.level.lower()]
    logger.setLevel(logger_level)

    redis = StrictRedis(host=config.redis.host, port=config.redis.port)
    handler = RedisHandler(redis, config.redis.key)
    formatter = UnionFormatter(app=app, format_style=format_style)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if config.stdout:
        # enables stdout logging
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logger_level)
        stdout_handler.setFormatter(
            Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s')  # TODO allow opt.
        )
        logger.addHandler(stdout_handler)

    if isinstance(extra_handlers, list):
        for h in extra_handlers:
            logger.addHandler(h)

    return logger


def get_logger(name=None):
    """Returns configured union instance
    """
    logger = logging.getLogger(name)

    if not [h for h in logger.handlers if type(h) == RedisHandler]:
        raise LookupError('Could not find Union logger with name {}'.format(name))

    return logger
