from sherlog import set_logger

log = set_logger('conf.yaml')

log.debug('info %s', 42)
log.info('info %s', 42)
log.warning('info %s', 42)
log.error('info %s', 42)
log.critical('info %s', 42)

try:
    1/0
except Exception as e:
    log.exception(e)
