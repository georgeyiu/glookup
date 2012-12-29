# glookup

`glookup` is a command Berkeley students use to look up their grades for computer science and electrical engineering classes on the instructional servers. Once the semester ends, however, instructional accounts are wiped and students no longer have access to those grades.

This is a simple script to save glookup data locally for future reference.

Dependency on `paramiko` for SSH.

```sudo easy_install paramiko```

### Usage

Standard `glookup` commands are supported. An extra argument is needed to specify the file in which the data resides locally.

First fetch the data from the servers:

```./glookup -f```

Follow on-screen directions. A file with the course name will be created in the current directory. This file should be used as the argument to the -c flag.

The following commands are then available:

```./glookup -c <filepath>```

```./glookup -c <filepath> -s <assignment>```

```./glookup -c <filepath> -s <assignment> -b <bucket>```
