### 0.1.0

- Initial "MVP" version


### 0.1.1

- Added PyYAML as a package dependency


### 0.1.2

- Project renamed to "Sherlog"

- Exception type in the monitor CLI is not renders in upper case

- Exception type and exception repr are now separated text fields in the DB

- Stacktrace is not a separated text field in the DB

- Thead ID and Process ID are not field of type BIGINT in DB
  Line is now of type INTEGER in DB

- Some DB field names is shorter now, type renamed to lvl (message level), changed some data types

    id       SERIAL NOT NULL PRIMARY KEY
    app      TEXT NOT NULL
    ts       TIMESTAMP NOT NULL
    ts_rel   INTEGER DEFAULT NULL
    lvl      TEXT NOT NULL
    message  TEXT DEFAULT NULL
    module   TEXT DEFAULT NULL
    function TEXT DEFAULT NULL
    line     INTEGER DEFAULT NULL
    path     TEXT DEFAULT NULL
    file     TEXT DEFAULT NULL
    pid      BIGINT DEFAULT NULL
    pname    TEXT DEFAULT NULL
    tid      BIGINT DEFAULT NULL
    tname    TEXT DEFAULT NULL
    logger   TEXT DEFAULT NULL
    ex_type  TEXT DEFAULT NULL
    ex_repr  TEXT DEFAULT NULL
    stack    TEXT DEFAULT NULL

- filter -> types from monitor config renamed to filter -> levels

- Some minor changes to monitor output styling for better readability ('\n' after exceptions, etc)


### 0.1.3

- Sherlog is now compatible with Python 2.7 (therefore type annotations in source code removed)


### 0.1.4

- Few fixes on Python 2.7 support (unicode issue, stack_info key error)


### 0.1.5

- Fixed critical bug in worker


### 0.1.6

- Fixed issue with log messages that contains formatting symbols such as '%' or {}
- format_style kwarg was removed from the sherlog.set_logger() signature


### 0.1.7

- Sherlog now creates functions in DB within the defined schema and not in public schema
- Added new parameter to client config main section. If 'dummy' is true, then no Redis handler
  will be attached to the logger. It may be a good idea during development, when you don't
  want to spam logs to Redis instance and DB while debug locally but still want to keep your
  code base as if Sherlog is there.


### 0.1.8

- Project dependecies versions are not strictly fixed anymore