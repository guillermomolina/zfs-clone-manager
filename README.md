# ZFS History Manager

Tool to manage ZFS with history metadata. The functionality is similar to Solaris beadm but generalized for any ZFS, not just ROOT and VAR.

## Usage

- Initialize zhm metadata

```bash
$ zhm -p /directory init rpool/directory
```

-p /directory -> mountpoint of the filesystem
rpool/directory -> root of the ZFS for clones and snapshots


- Show zhm metadata

```bash
$ cd /directory
$ zhm ls
```

- Create new clones (derived from active)

```bash
$ zhm create
$ zhm create
```

- Start using the previously created clone

```bash
$ zhm activate 00000002
```

- All the clones are visible at <mountpoint>/.clones

```bash
$ ls .clones
00000001 00000002 00000003
```


- Remove clones

```bash
$ zhm rm 00000001
```

