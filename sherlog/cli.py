# coding=utf-8

"""
Sherlog command line tool
"""

import os

import click

from sherlog.config import SherlogBackendConfig
from sherlog.config import SherlogMonitorConfig

from sherlog.monitor import SherlogMonitor
from sherlog.worker import SherlogWorker


# See http://click.pocoo.org/dev/python3/#unicode-literals for more details.
click.disable_unicode_literals_warning = True


def print_header():
    click.echo()
    click.echo('-'*80)
    click.secho('SHERLOG. Plug and play log aggregation made easy.', bold=True, fg='green')
    click.echo('-'*80)
    click.echo()


def config_from_arg(arg, config_type):
    name, ext = os.path.splitext(arg)

    if ext.lower() == '.yaml':
        config = config_type.from_yaml(arg)
    elif ext.lower() == '.json':
        config = config_type.from_json(arg)
    else:
        raise ValueError('Unsupported config file extension (use JSON or YAML): {}'.format(ext))

    return config


@click.group()
def main():
    """Sherlog command line tool."""
    pass


@main.command()
@click.option('--backend', '-b', default='psql', type=str, help='Sherlog backend')  # psql default
@click.option('--config', '-c', type=str, required=True, help='Sherlog backend config')
def worker(backend, config):
    """Sherlog worker instance"""
    print_header()

    config = config_from_arg(config, SherlogBackendConfig)

    instance = SherlogWorker(backend=backend, config=config)

    click.secho('Monitoring REDIS instance on {}:{} | Key: {} ... OK'.format(
        config.redis.host, config.redis.port, config.redis.key), fg='green')

    while True:
        instance.work()


@main.command()
@click.option('--backend', '-b', default='psql', type=str, help='Sherlog backend')  # psql default
@click.option('--config', '-c', type=str, required=True, help='Sherlog backend config')
def monitor(backend, config):
    """Sherlog global monitor CLI"""

    def echo_event(e, cfg, separator):
        color_map = {
            '[D]': 'white',
            '[I]': 'green',
            '[W]': 'yellow',
            '[E]': 'red',
            '[C]': 'red'
        }

        ex_type, ex_repr, stack = e.pop('ex_type'), e.pop('ex_repr'), e.pop('stack')

        e['lvl'] = '[' + e['lvl'][0].upper() + ']'
        e['ts'] = e['ts'].replace('T', ' ')[:19]

        if not cfg.filters.fields:  # then default
            default = ['lvl', 'ts', 'app', 'module', 'message']
            tokens = [e[i] for i in default]
        else:
            tokens = [e[i] for i in cfg.filters.fields]

        if ex_type or stack:
            click.echo('\n')

        click.secho(separator.join(tokens),
                    fg=color_map[e['lvl']],
                    bg='white' if e['lvl'] == '[C]' else None,
                    bold=True)

        if ex_type and ex_repr:
            head = '===== {} ====='.format(ex_type)
            while len(head) < 80:
                head += '='
            click.secho(head, fg='red', bold=True)
            click.echo(ex_repr)
            click.echo('\n')

        if stack:
            head = '===== STACK INFO ====='
            while len(head) < 80:
                head += '='
            click.secho(head, fg='yellow', bold=True)
            click.echo(stack)
            click.echo('\n')

    def filtered(e, cfg):
        return not all([
            e['app'] in cfg.filters.apps if cfg.filters.apps is not None else True,
            e['lvl'] in cfg.filters.levels if cfg.filters.levels is not None else True,
            e['logger'] in cfg.filters.loggers if cfg.filters.loggers is not None else True
        ])

    print_header()

    config = config_from_arg(config, SherlogMonitorConfig)

    click.secho('Monitoring PostgreSQL instance on {}:{} | Database: {} Channel: {} ... OK'.format(
        config.postgresql.host, config.postgresql.port,
        config.postgresql.database, '{}_{}_updates'.format(config.postgresql.schema,
                                                           config.postgresql.table)), fg='green')
    click.echo('\n')

    for event in SherlogMonitor(config=config).listen():
        if not filtered(event, config):
            echo_event(event, config, separator=' | ')
