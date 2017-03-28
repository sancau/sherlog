## Sherlog. Log aggregation made easy.
#### Aggregate your log messages from decoupled applications in an easy plug-and-play manner

##### Based on Redis and PostgreSQL. Requires almost zero configuration.
##### Sherlog provides ability to aggregate, store and monitor logging messages from different Python applications and modules in real time.

## Getting started
### pip install sherlog

### 1. Using from Python application

``` python
import sherlog

config = {
  'app': 'sherlog_example'  # your application name
  'level': 'debug',  # top level for logging (look Python logging module documentation for details)
  'stdout': True  # if True then default StreamHandler will be added (to see logging in your app stdout)
  'dummy': False  # if True then no Redis handler will be attached to Sherlog logger (dummy mode
  may useful during development)

  'redis': {
    'host': localhost,  
    'port': 6379,
    'key': 'sherlog'  # this key will be used by Sherlog to forward messages through Redis
  }
}

log = sherlog.set_logger(config, name='MyLoggerName')  # if no name was passed the 'root' logger will be returned
```

set_logger() signature: 

```python
set_logger(config, name=None, extra_handlers=None)
```

The object returned by sherlog.set_logger() is an instance of Python logger.
So all the behavior that you might expect from Python logger is there.
Under the hood Sherlog will add a handler to the logger that will allow it to forward
messages to your REDIS server. The SherlogHandler also uses special Formatter class
that basically transforms all the information Python logger provides to a dict (JSON) object.
It will also add the application name that we defined in the config above.

- Note: The Python logger is a singleton. Therefore Sherlog will restrict setting a logger with the same
  name more then once in runtime. You still can get an instance that is already configured by Sherlog
  (for example in some sub module of your app) by calling sherlog.get_logger('your logger name').
  ``` python
  log = sherlog.get_logger('MyLoggerName')
  ```
 
- Note: You can add arbitrary number of custom handlers along with Sherlog handler by passing them to
  extra_handlers key-value argument.

- Note: There is a limitation in version (0.1.6): Python logging 'extra' kwag is not supported yet.

From here you can use the logger exactly you would use Python default logger:

```python
log.debug('Starting the party...')
log.info('Party in progress.')
log.warning('Guest number %s is too drunk', 42)
log.error('Out of beer.', stack_info=True)
log.critical('Wookie in the house!')
try:
    if wookie_in_the_house:
        raise WookieInTheHouse('Big wookie!!!')
except WookieInTheHouse as e:
    log.exception(e)
```

### 2. Sherlog worker (REDIS to PostgreSQL layer)

Now then you know how to plug in Sherlog into your Python application it is time to
make the logs actually being forwarded to PostgreSQL.

Sherlog provides simple CLI tool to start up a worker (or many workers)
in a separate process (or even from remote machine).

The config the worker will expect can be specified as a YAML or JSON file.
Here is an example of YAML config:

``` yaml
redis:
  host: localhost
  port: 6379
  key: sherlog
 
postgresql:
  host: localhost
  port: 5432
  database: <your db name>
  user: <username>
  password: <password>
  schema: sherlog
  table: logs
```

To start the worker instance simply run in the console:

```shell
sherlog worker -c <path_to_your_config_file>
```
The worker will look for specified schema and table in the PostgreSQL DB and if need will 
automatically create the schema and table of required structure.

NOTE: All the user input related to the PostgreSQL will be sanitized to prevent possible SQL injection.

After the worker is done with all the connections and preparations you should see a success message. 
The worker will be monitoring the specified REDIS instance and key.
When the message will be received from REDIS the worker will insert the event to the specified PostgreSQL schema/table.
Under the hood Sherlog uses REDIS lpush - brpop to ensure that every message will be inserted just once even
if you are using multiple instances of workers (if one is not enough to process all the incoming messages from your apps).

### 3. Sherlog monitor CLI

#### coming soon...

