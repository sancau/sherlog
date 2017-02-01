## Union. Logs aggregation made easy.
#### Aggregate your log messages from decoupled applications in an easy plug-and-play manner

##### Based on Redis and PostgreSQL. Requires almost zero configuration.
##### Union provides ability to aggregate, store and monitor logging messages from different Python applications and modules in real time.

## Getting started
### pip install union

### 1. Using from Python application

``` python
import union

config = {
  'app': 'union_example'  # your application name
  'level': 'debug',  # top level for logging (look Python logging module documentation for details)
  'stdout': True  # if True then default StreamHandler will be added (to see logging in your app stdout)

  'redis': {
    'host': localhost,  
    'port': 6379,
    'key': 'union'  # this key will be used by Union to forward messages through Redis
  }
}

log = union.set_logger('MyLoggerName', config=config)  # if no name was passed the 'root' logger will be returned
```

set_logger() signature: 

```python
set_logger(name=None, *, config, format_style='%', extra_handlers=None)
```

The object returned by union.set_logger() is an instance of Python logger.
So all the behavior that you might expect from Python logger is there.
Under the hood Union will add a handler to the logger that will allow it to forward
messages to your REDIS server. The Union RedisHandler also uses special Formatter class
that basicaly trasforms all the information Python logger provides to a dict (JSON) object.
It will also add the application name that we defined in the config above.

- Note: The Python logger is a singleton. Therefore Union will restrict setting a logger with the same
  name more then once in runtime. You still can get an instance that is already configured by Union 
  (for example in some submodule of your app) by calling union.get_logger('your logger name').
  ``` python
  log = union.get_logger('MyLoggerName')
  ```
 
- Note: You can add arbitary number of custom handlers along with Union handler by passing them to
  extra_handlers key-value argument.

- Note: In the current version (0.1.1) only '%' formatting style is supported. format_style argument is added 
  in advance for future extensions and should not be used.
  
- Note: Another limitation of version (0.1.1): Python logging 'extra' kwag is not supported yet.

From here you can use the logger exactly you would use Python default logger:

```python
log.debug('Starting the party...')
log.info('Party in progress.')
log.warning('Guest numer %s is too drunk', 42)
log.error('Out of beer.', stack_info=True)
log.critical('Wookie in the house!')
try:
    if wookie_in_the_house:
        raise WookieInTheHouse('Big wookie!!!')
except WookieInTheHouse as e:
    log.exception(e)
```

### 2. Union worker (REDIS to PostgreSQL layer)

Now then you know how to plug in Union into your Python application it is time to 
make the logs actually being forwarded to PostgreSQL.

Union provides simple CLI tool to start up a worker (or many workers) 
in a separate process (or even from remote machine).

The config the woker will expect can be specified as a YAML or JSON file. 
Here is an example of YAML config:

``` yaml
redis:
  host: localhost
  port: 6379
  key: union
 
postgresql:
  host: localhost
  port: 5432
  database: <your db name>
  user: <username>
  password: <password>
  schema: union 
  table: logs
```

To start the worker instance simply run in the console:

```shell
union worker -c <path_to_your_cofig_file>
```
The worker will look for specified schema and table in the PostgreSQL DB and if need will 
automaticaly create the schema and table of required structure. 

NOTE: All the user input related to the PostgreSQL will be sanitized to prevent possible SQL injection.

After the worker is done with all the connections and preparations you should see a success message. 
The worker will be monitoring the specified REDIS instance and key.
When the message will be recieved from REDIS the worker will insert the event to the specified PostgreSQL schema/table.
Under the hood Union uses REDIS lpush - brpop to ensure that every message will be inserted just once even
if you are using multiple instances of workers (if one is not enough to process all the incoming messages from your apps).

### 3. Union monitor


