# ZFS History Manager

Tool to manage ZFS with history metadata. The functionality is similar to Solaris beadm but generalized for any ZFS, not just ROOT and VAR.

## Usage

- Initialize zhm metadata

```bash
$ zhm -p /directory init rpool/directory
ZHM initialized ZFS rpool/directory at path /directory
```

-p /directory -> mountpoint of the filesystem
rpool/directory -> root of the ZFS for clones and snapshots


- Show zhm metadata

```bash
$ cd /directory
$ zhm ls
A  ID        MOUNTPOINT  ORIGIN  DATE               
*  00000000  /directory          2021-02-14 04:45:47
```

- Create new clones (derived from active)

```bash
$ cd /directory
$ zhm create
Created instance 00000001 at path /directory/.clones/00000001
$ zhm create
Created instance 00000002 at path /directory/.clones/00000002
```

- Start using the previously created clone

```bash
$ zhm -p /directory activate 00000002
Activated instance 00000002
```

The activate command can not be executed inside the mountpoint, therefore the parameter -p <mounpoint> is mandatory.  

- All the clones are visible at <mountpoint>/.clones

```bash
$ cd /directory
$ ls .clones
0000000 00000001 00000002
```


- Remove clones

```bash
$ cd /directory
$ zhm rm 00000001
```

