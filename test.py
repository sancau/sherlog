# coding=utf-8

from sherlog import set_logger

log = set_logger('conf.yaml')

log.debug('info %s', 42)
log.info('info %s', 42)
log.warning('info %s', 42)
log.error('info %s', 42)
log.critical('info %s', 42)

log.debug('кирилица %s', 42)
log.info('кирилица %s', 42)
log.warning('кирилица %s', 42)
log.error('кирилица %s', 42)
log.critical('кирилица %s', 42)

log.debug(u'кирилица юникод %s', 42)
log.info(u'кирилица юникод %s', 42)
log.warning(u'кирилица юникод %s', 42)
log.error(u'кирилица юникодs %s', 42)
log.critical(u'кирилица юникод %s', 42)

try:
    1/0
except Exception as e:
    log.exception(e)


