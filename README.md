# glookup

`glookup` is a command Berkeley students use to look up their grades on instructional servers for computer science and electrical engineering courses. Once the semester ends, however, instructional accounts are wiped and students no longer have access to their grades.

This is a simple script to save glookup data locally for future reference.

Dependency on `paramiko` for SSH.

```sudo easy_install paramiko```

Most of the standard `glookup` commands are supported. Multiple assignment lookup is not supported because database access is required. An extra argument is needed to specify the file in which the data resides locally.

### Usage

First fetch the data from the servers:

```python glookup.py -f```

Follow on-screen directions. A file with the course name will be created in the current directory. This file should be used as the argument to the -c flag.

The following commands are then available:

```python glookup.py -c <filepath>```

```python glookup.py -c <filepath> -s <assignment>```

```python glookup.py -c <filepath> -s <assignment> -b <bucket>```
