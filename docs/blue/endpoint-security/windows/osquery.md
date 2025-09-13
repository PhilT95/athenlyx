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