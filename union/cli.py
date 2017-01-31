# coding=utf-8
"""
Union command line tool
"""
import os

import click

from union.config import UnionBackendConfig
from union.config import UnionMonitorConfig

from union.monitor import UnionMonitor
from union.worker import UnionWorker


# See http://click.pocoo.org/dev/python3/#unicode-literals for more details.
click.disable_unicode_literals_warning = True


def print_header():
    click.echo()
    click.echo('-'*80)
    click.secho('UNION. Plug and play log aggregation made easy.', bold=True, fg='green')
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
    """Union command line tool."""
    pass


@main.command()
@click.option('--backend', '-b', default='psql', type=str, help='Union backend')  # psql default
@click.option('--config', '-c', type=str, required=True, help='Union backend config')
def worker(backend, config):
    """Union worker instance"""
    print_header()

    config = config_from_arg(config, UnionBackendConfig)

    instance = UnionWorker(backend=backend, config=config)

    click.secho('Monitoring REDIS instance on {}:{} | Key: {} ... OK'.format(
        config.redis.host, config.redis.port, config.redis.key), fg='green')

    while True:
        instance.work()


@main.command()
@click.option('--backend', '-b', default='psql', type=str, help='Union backend')  # psql default
@click.option('--config', '-c', type=str, required=True, help='Union backend config')
def monitor(backend, config):
    """Union global monitor CLI"""

    def echo_event(e: dict, cfg: UnionMonitorConfig, separator: str):
        color_map = {
            '[D]': 'white',
            '[I]': 'green',
            '[W]': 'yellow',
            '[E]': 'red',
            '[C]': 'red'
        }

        exception, stacktrace = e.pop('exception'), e.pop('stacktrace')

        e['type'] = '[' + e['type'][0].upper() + ']'
        e['timestamp'] = e['timestamp'].replace('T', ' ')[:-4]

        if not cfg.filters.fields:  # then default
            default = ['type', 'timestamp', 'app', 'module', 'message']
            tokens = [e[i] for i in default]
        else:
            tokens = [e[i] for i in cfg.filters.fields]

        click.secho(separator.join(tokens),
                    fg=color_map[e['type']],
                    bg='white' if e['type'] == '[C]' else None,
                    bold=True)

        if exception:
            head = '===== {} ====='.format(exception['type'].upper())
            while len(head) < 80:
                head += '='
            click.secho(head, fg='red', bold=True)
            click.echo(exception['repr'])
            click.echo('\n')

        if stacktrace:
            head = '===== STACK INFO ====='
            while len(head) < 80:
                head += '='
            click.secho(head, fg='yellow', bold=True)
            click.echo(stacktrace['repr'])
            click.echo('\n')

    def filtered(e, cfg: UnionMonitorConfig):
        return not all([
            e['app'] in cfg.filters.apps if cfg.filters.apps is not None else True,
            e['type'] in cfg.filters.types if cfg.filters.types is not None else True,
            e['logger'] in cfg.filters.loggers if cfg.filters.loggers is not None else True
        ])

    print_header()

    config = config_from_arg(config, UnionMonitorConfig)

    click.secho('Monitoring PostgreSQL instance on {}:{} | Database: {} Channel: {} ... OK'.format(
        config.postgresql.host, config.postgresql.port,
        config.postgresql.database, '{}_{}_updates'.format(config.postgresql.schema,
                                                           config.postgresql.table)), fg='green')

    for event in UnionMonitor(config=config).listen():
        if not filtered(event, config):
            echo_event(event, config, separator=' | ')
