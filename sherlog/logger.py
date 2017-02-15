# coding=utf-8

import json
import logging
import os
import sys

from datetime import datetime

from logging import Handler
from logging import Formatter

from redis import StrictRedis

from sherlog.config import SherlogClientConfig


LVL_MAP = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}


class SherlogHandler(Handler):
    """Handler meant to use REDIS lpush rpop pattern
    """
    def __init__(self, redis, key):
        self.redis = redis
        self.key = key
        super(SherlogHandler, self).__init__()

    def emit(self, record):
        try:
            log_entry = self.format(record)
            json_entry = json.dumps(log_entry)
            self.redis.lpush(self.key, json_entry)
        except Exception as e:
            print(e)  # TODO logging


class SherlogFormatter(Formatter):
    """Sherlog sherlog formatter. Performs log event pre processing.
    """
    def __init__(self, app, format_style='%'):
        supported_styles = ['%', ]
        if format_style not in supported_styles:
            raise ValueError('Given format style is not supported.')

        self.app = app
        self.format_style = format_style

        super(SherlogFormatter, self).__init__()

    def format_message(self, record):
        if self.format_style == '%':
            try:
                # TODO this might be an overhead (compare Python 2 / 3 logging)
                return str(record.msg) % record.args
            except UnicodeEncodeError:
                return record.msg % record.args
        else:
            raise NotImplementedError('Unexpected formatting style.')

    def format(self, record):
        ts = datetime.fromtimestamp(record.created).isoformat()

        data = {
            'lvl': record.levelname.lower(),
            'ts': ts,
            'ts_rel': round(record.relativeCreated / 1000, 3),  # seconds
            'app': self.app,
            'pid': record.process,
            'pname': record.processName,
            'tid': record.thread,
            'tname': record.threadName,
            'file': record.filename,
            'path': record.pathname,
            'module': record.module,
            'logger': record.name,
            'function': record.funcName,
            'line': record.lineno,
            'message': self.format_message(record),
            'ex_type': None,
            'ex_repr': None,
            'stack': None
        }

        if record.exc_info:
            data['ex_type'] = record.exc_info[0].__name__,  # type of exception (class name)
            data['ex_repr'] = self.formatException(record.exc_info)
        if record.stack_info:
            data['stack'] = self.formatStack(record.stack_info)

        return data


def set_logger(config, name=None, format_style='%', extra_handlers=None):  # TODO more f.
    # styles
    """Initializes sherlog logger configuration"""
    logger = logging.getLogger(name)

    if [h for h in logger.handlers if type(h) == SherlogHandler]:
        raise ValueError('Logger with name {} is already initialized by Sherlog.'.format(name))

    if isinstance(config, dict):
        config = SherlogClientConfig(dict_config=config)
    elif isinstance(config, str):
        ext = os.path.splitext(config)[1]
        if ext.lower() == '.yaml':
            config = SherlogClientConfig.from_yaml(config)
        elif ext.lower() == '.json':
            config = SherlogClientConfig.from_json(config)
        else:
            raise ValueError('Unsupported config file extension: {}'.format(ext))
    else:
        raise ValueError('Sherlog config should be either Python Dict, .yaml file or .json file')

    app = config.app

    logger_level = LVL_MAP[config.level.lower()]
    logger.setLevel(logger_level)

    redis = StrictRedis(host=config.redis.host, port=config.redis.port)
    handler = SherlogHandler(redis, config.redis.key)
    formatter = SherlogFormatter(app=app, format_style=format_style)
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
    """Returns configured sherlog instance
    """
    logger = logging.getLogger(name)

    if not [h for h in logger.handlers if type(h) == SherlogHandler]:
        raise LookupError('Could not find Sherlog logger with name {}'.format(name))

    return logger
