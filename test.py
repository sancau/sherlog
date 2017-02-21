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
log.error(u'кирилица юникод %s', 42)
log.critical(u'кирилица юникод %s', 42)

log.info("""
http://sap-pop-cntr.sap.ulmart.ru:50000/XISOAPAdapter/MessageServlet?senderParty=&senderService=BC_SITE&receiverParty=&receiverService=&interface=si_getGoodsState_outb&interfaceNamespace=urn%3A%2F%2Fulmart.ru%2Fpi%2FSITE
""")

log.error(r"""
2017-02-17    17:30:58    ЗАГРУЗКА ОЖИДАНИЙ    CRITICAL    Traceback (most recent call last):
  File "C:/Users/abetkin.v.v/PycharmProjects/speed/get_ozhidanie.py", line 27, in <module>
    tovar_updater.update_tovars_and_add_oz()
  File "C:\Users\abetkin.v.v\PycharmProjects\speed\modules\load_in_base\tovar_updater.py", line 142, in update_tovars_and_add_oz
    commiting_session.commit()
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\orm\scoping.py", line 157, in do
    return getattr(self.registry(), name)(*args, **kwargs)
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\orm\session.py", line 801, in commit
    self.transaction.commit()
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\orm\session.py", line 392, in commit
    self._prepare_impl()
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\orm\session.py", line 372, in _prepare_impl
    self.session.flush()
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\orm\session.py", line 2019, in flush
    self._flush(objects)
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\orm\session.py", line 2137, in _flush
    transaction.rollback(_capture_exception=True)
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\util\langhelpers.py", line 60, in __exit__
    compat.reraise(exc_type, exc_value, exc_tb)
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\orm\session.py", line 2101, in _flush
    flush_context.execute()
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\orm\unitofwork.py", line 373, in execute
    rec.execute(self)
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\orm\unitofwork.py", line 532, in execute
    uow
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\orm\persistence.py", line 174, in save_obj
    mapper, table, insert)
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\orm\persistence.py", line 767, in _emit_insert_statements
    execute(statement, multiparams)
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\engine\base.py", line 914, in execute
    return meth(self, multiparams, params)
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\sql\elements.py", line 323, in _execute_on_connection
    return connection._execute_clauseelement(self, multiparams, params)
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\engine\base.py", line 1010, in _execute_clauseelement
    compiled_sql, distilled_params
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\engine\base.py", line 1146, in _execute_context
    context)
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\engine\base.py", line 1341, in _handle_dbapi_exception
    exc_info
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\util\compat.py", line 200, in raise_from_cause
    reraise(type(exception), exception, tb=exc_tb, cause=cause)
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\engine\base.py", line 1116, in _execute_context
    context)
  File "C:\Users\abetkin.v.v\PycharmProjects\PYTHON_VIRTUAL_ENVS\speed\lib\site-packages\sqlalchemy\engine\default.py", line 447, in do_executemany
    cursor.executemany(statement, parameters)
IntegrityError: (psycopg2.IntegrityError) ОШИБКА:  повторяющееся значение ключа нарушает ограничение уникальности "oz_city_pkey"
""")

try:
    1/0
except Exception as e:
    log.exception(e, stack_info=True)


