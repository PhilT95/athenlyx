# OSquery

**OSquery** is an open-soruce agent created by Facebook in 2014. It converts the operating system into a relational database and allows to ask questions from the tables using SQL queries like:

- returning the list of running processes
- a user account created on the host
- process of communicating with certain suspicious domains

It is widely used by Security Analysts, Incident Responders etc. and can be used  on multiple platforms like

- Windows
- Linux
- MacOS
- FreeBSD

## Basics of OSquery

One way to interact with **OSquery** is the interactive mode. It can be used with a terminal by running the ``osqueryi`` binary. The ``.help`` parameter provides more information.

```pwsh-session
PS C:\Users\Administrator> osqueryi
Using a [1mvirtual database[0m. Need help, type '.help'
osquery> .help
Welcome to the osquery shell. Please explore your OS!
You are connected to a transient 'in-memory' virtual database.

.all [TABLE]     Select all from a table
.bail ON|OFF     Stop after hitting an error
.connect PATH    Connect to an osquery extension socket
.disconnect      Disconnect from a connected extension socket
.echo ON|OFF     Turn command echo on or off
.exit            Exit this program
.features        List osquery's features and their statuses
.headers ON|OFF  Turn display of headers on or off
.help            Show this message
.mode MODE       Set output mode where MODE is one of:
                   csv      Comma-separated values
                   column   Left-aligned columns see .width
                   line     One value per line
                   list     Values delimited by .separator string
                   pretty   Pretty printed SQL results (default)
.nullvalue STR   Use STRING in place of NULL values
.print STR...    Print literal STRING
.quit            Exit this program
.schema [TABLE]  Show the CREATE statements
.separator STR   Change separator used by output mode
.socket          Show the local osquery extensions socket path
.show            Show the current values for various settings
.summary         Alias for the show meta command
.tables [TABLE]  List names of tables
.types [SQL]     Show result of getQueryColumns for the given query
.width [NUM1]+   Set column widths for "column" mode
.timer ON|OFF      Turn the CPU timer measurement on or off
osquery>
```

You can list the tables that can be queried using the ``.tables`` command. 

```pwsh-session
osquery> .table
  => appcompat_shims
  => arp_cache
  => atom_packages
  => authenticode
  => autoexec
  => azure_instance_metadata
  => azure_instance_tags
  => background_activities_moderator
  => bitlocker_info
  => carbon_black_info
  => carves
  => certificates
  => chassis_info
```

??? tip "Getting tables associated with a process"
    If you want to see what tables are associated with a process, the parameter can be extended with the process ``.tables process``.

To list all tables with the term ``user``, the parameter ``.tables user`` can be used.

```pwsh-session
osquery> .table user
  => user_groups
  => user_ssh_keys
  => userassist
  => users
```

### Table Schema

Just knowing the table names is not enough to understand what information it contains without actually querying it. Therefore knowledge of columns and types, known as **schema**, for each table is also helpful. A table's schema can be listed using the command ``.schema``.

```pwsh-session
osquery> .schema users
CREATE TABLE users(`uid` BIGINT, `gid` BIGINT, `uid_signed` BIGINT, `gid_signed` BIGINT, `username` TEXT, `description` TEXT, `directory` TEXT, `shell` TEXT, `uuid` TEXT, `type` TEXT, `is_hidden` INTEGER HIDDEN, `pid_with_namespace` INTEGER HIDDEN, PRIMARY KEY (`uid`, `username`, `uuid`, `pid_with_namespace`)) WITHOUT ROWID;
```

This example shows the schema for the ``users`` table. Based on this information a few columns can be selected using an SQL query.

```pwsh-session
osquery> select gid, uid, description, username, directory from users;
+-----+------+-------------------------------------------------------------------------------------------------+--------------------+---------------------------------------------+
| gid | uid  | description                                                                                     | username           | directory                                   |
+-----+------+-------------------------------------------------------------------------------------------------+--------------------+---------------------------------------------+
| 544 | 1008 |                                                                                                 | 4n6lab             |                                             |
| 544 | 500  | Built-in account for administering the computer/domain                                          | Administrator      | C:\Users\Administrator                      |
| 544 | 1010 |                                                                                                 | art-test           |                                             |
| 581 | 503  | A user account managed by the system.                                                           | DefaultAccount     |                                             |
| 546 | 501  | Built-in account for guest access to the computer/domain                                        | Guest              |                                             |
| 544 | 1009 | User 01                                                                                | User01             | C:\Users\User01                            |
| 513 | 504  | A user account managed and used by the system for Windows Defender Application Guard scenarios. | WDAGUtilityAccount |                                             |
| 18  | 18   |                                                                                                 | SYSTEM             | %systemroot%\system32\config\systemprofile  |
| 19  | 19   |                                                                                                 | LOCAL SERVICE      | %systemroot%\ServiceProfiles\LocalService   |
| 20  | 20   |                                                                                                 | NETWORK SERVICE    | %systemroot%\ServiceProfiles\NetworkService |
+-----+------+-------------------------------------------------------------------------------------------------+--------------------+---------------------------------------------+
```

The [Official Documentation](https://osquery.io/schema/5.19.0) provides more detailed information about the schemas used.

### Display Mode

OSquery comes with multiple display modes. Refer to the ``.help`` function or the example below.

```pwsh-session
osquery> .help
.mode MODE       Set output mode where MODE is one of:
                   csv      Comma-separated values
                   column   Left-aligned columns see .width
                   line     One value per line
                   list     Values delimited by .separator string
                   pretty   Pretty printed SQL results (default)
```

## SQL Queries

The SQL language implemented in **OSquery** is not an entire SQL language that is usually used, but rather a superset of SQLite.

Most of the time, the queries start with the **SELECT** statement, because OSquery only queries information on an endpoint. There is no updating of information or data.

!!! note
    Statements like **UPDATE** and **DELETE** can be used, but only when run-time tables (views) are created or an extensions is used that supports this.

### Exploring Installed Programs

To retrieve all information about the installed programs on the endpoint, the schema needs to be known and understood using the ``.schema programs`` or by using the documentation [here](https://osquery.io/schema/5.5.1/#programs).

```pwsh-session
osquery> SELECT * FROM programs LIMIT 1;
+-------------------+---------+------------------+----------------------------------------------------------------------------+----------+---------------------+------------------------------------------------------+--------------+----------------------------------------+
| name              | version | install_location | install_source                                                             | language | publisher           | uninstall_string                                     | install_date | identifying_number                     |
+-------------------+---------+------------------+----------------------------------------------------------------------------+----------+---------------------+------------------------------------------------------+--------------+----------------------------------------+
| aws-cfn-bootstrap | 2.0.5   |                  | C:\ProgramData\Package Cache\{2C9F7E98-B055-4344-B8E4-58996F4A3B00}v2.0.5\ | 1033     | Amazon Web Services | MsiExec.exe /X{2C9F7E98-B055-4344-B8E4-58996F4A3B00} | 20210311     | {2C9F7E98-B055-4344-B8E4-58996F4A3B00} |
+-------------------+---------+------------------+----------------------------------------------------------------------------+----------+---------------------+------------------------------------------------------+--------------+----------------------------------------+
```

!!! note
    The ``LIMIT`` parameter has been used to keep the example short.

Specific columns can also be selected than retrieving every column of the table.

```pwsh-session
osquery> SELECT name, version, install_location, install_date from programs limit 1;
+-------------------+---------+------------------+--------------+
| name              | version | install_location | install_date |
+-------------------+---------+------------------+--------------+
| aws-cfn-bootstrap | 2.0.5   |                  | 20210311     |
+-------------------+---------+------------------+--------------+
```

### Count Function

To see how many programs or entries are in any table that are returned, the ``count()`` function can be used.

```pwsh-session
osquery> SELECT count(*) from programs;
+----------+
| count(*) |
+----------+
| 19       |
+----------+
```

### WHERE Function

``WHERE`` can be used to narrow down the list of results returned based on a specific criteria. The following example will first get the user table and only display the result for the user *Administrator*.

```pwsh-session
osquery> SELECT * FROM users WHERE username='Administrator';
+-----+-----+------------+------------+---------------+--------------------------------------------------------+------------------------+-----------------------------+---------------------------------------------+-------+
| uid | gid | uid_signed | gid_signed | username      | description                                            | directory              | shell                       | uuid                                        | type  |
+-----+-----+------------+------------+---------------+--------------------------------------------------------+------------------------+-----------------------------+---------------------------------------------+-------+
| 500 | 544 | 500        | 544        | Administrator | Built-in account for administering the computer/domain | C:\Users\Administrator | C:\Windows\system32\cmd.exe | S-1-5-21-1966530601-3185510712-10604624-500 | local |
+-----+-----+------------+------------+---------------+--------------------------------------------------------+------------------------+-----------------------------+---------------------------------------------+-------+
```

The following filtering options exist.

|Operator|Description|
|:-------|-----------|
|``=``|Equal|
|``<>``|Not Equal|
|``>`` & ``>=``|Greater than & Greater than or equal to|
|``<`` & ``<=``|Less than & less than or equal to|
|``BETWEEN``|Between a range|
|``LIKE``|Pattern wildcard searches|
|``%``|Wildcard for multiple characters|
|``_``|Wildcard for one character|

The wildcard rules for folder structures works as follows

- ``%``: Match all files and folders for one level
- ``%%``: Match all files anf folders recursively
- ``%abc``: Match all within-level ending in **abc**
- ``abc%``: Match all within-level starting with **abc**


!!! warning
    Some tables *require* a ``WHERE`` clause, such as the **file** table.

    ```pwsh-session
    osquery> select * from file;
    W0915 20:26:47.930963  5008 virtual_table.cpp:965] Table file was queried without a required column in the WHERE clause
    W0915 20:26:47.945974  5008 virtual_table.cpp:976] Please see the table documentation: https://osquery.io/schema/#file
    Error: constraint failed
    ```

### JOIN Function

OSquery can also be used to join 2 tables based on a column that is shared by both.

```pwsh-session
osquery> select p.pid, p.name, p.path, u.username from processes p JOIN users u on u.uid=p.uid LIMIT 10;
+------+-------------------------+---------------------------------------------------------------------------------+----------+
| pid  | name                    | path                                                                            | username |
+------+-------------------------+---------------------------------------------------------------------------------+----------+
| 968  | rdpclip.exe             | C:\Windows\System32\rdpclip.exe                                                 | Administrator    |
| 888  | svchost.exe             | C:\Windows\System32\svchost.exe                                                 | Administrator    |
| 2904 | sihost.exe              | C:\Windows\System32\sihost.exe                                                  | Administrator    |
| 1332 | svchost.exe             | C:\Windows\System32\svchost.exe                                                 | Administrator    |
| 3908 | taskhostw.exe           | C:\Windows\System32\taskhostw.exe                                               | Administrator    |
| 3828 | ctfmon.exe              | C:\Windows\System32\ctfmon.exe                                                  | Administrator    |
| 5524 | explorer.exe            | C:\Windows\explorer.exe                                                         | Administrator    |
| 1280 | ShellExperienceHost.exe | C:\Windows\SystemApps\ShellExperienceHost_cw5n1h2txyewy\ShellExperienceHost.exe | Administrator    |
| 5620 | SearchUI.exe            | C:\Windows\SystemApps\Microsoft.Windows.Cortana_cw5n1h2txyewy\SearchUI.exe      | Administrator    |
| 5736 | RuntimeBroker.exe       | C:\Windows\System32\RuntimeBroker.exe                                           | Administrator    |
+------+-------------------------+---------------------------------------------------------------------------------+----------+
```


