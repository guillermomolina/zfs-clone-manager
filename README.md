# ZFS History Manager

Tool to add version control and historic data of a directory with ZFS. The functionality is similar to Solaris beadm but generalized for any ZFS filesystem, not just ROOT and VAR.

The suggested workflow is:
1. Initialize (zhm init)
2. Make changes in active
3. Clone (zhm clone)
4. Make changes in clone
5. Activate clone (zhm activate)
6. [Remove older clones (zhm rm)]
7. Go to step 2

## Usage

- Initialize ZHM

```bash
$ zhm -p /directory init rpool/directory
ZHM initialized ZFS rpool/directory at path /directory
```

"-p /directory" -> path of the filesystem (mountpoint of the active clone).

"rpool/directory" -> root of the ZFS for clones and snapshots.


- Show ZHM information

```bash
$ cd /directory
$ zhm ls
A  ID        MOUNTPOINT  ORIGIN  DATE               
*  00000000  /directory          2021-02-14 04:45:47
```

- Create new clones (derived from active)

```bash
$ cd /directory
$ zhm clone
Created instance 00000001 at path /directory/.clones/00000001
$ zhm clone
Created instance 00000002 at path /directory/.clones/00000002
```

- Activate the previously created clone, mounting it at ZHM path 

```bash
$ zhm -p /directory activate 00000002
Activated instance 00000002
```

The activate command can not be executed from inside the path, therefore the parameter -p <path> is mandatory.  

- All the clones are visible at <path>/.clones

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


- Destroy ZHM related data

This is dangerous, you should backup data first.

```bash
$ zhm -p /directory destroy        
WARNING!!!!!!!!
All the filesystems, clones, snapshots and directories associated with /directory will be permanently deleted.
This operation is not reversible.
Do you want to proceed? (yes/NO) yes
Destroyed ZHM at path /directory
```
