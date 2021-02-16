# ZFS Clone Manager

Tool to add version control and historic data of a directory with ZFS. The functionality is similar to Solaris beadm but generalized for any ZFS filesystem, not just ROOT and VAR.

The suggested workflow is:
1. Initialize (zcm init)
2. Make changes in active
3. Clone (zcm clone)
4. Make changes in clone
5. Activate clone (zcm activate)
6. [Remove older clones (zcm rm)]
7. Go to step 2

## Usage

- Initialize ZCM

```bash
$ zcm -p /directory init rpool/directory
ZCM initialized ZFS rpool/directory at path /directory
```

"-p /directory" -> path of the filesystem (mountpoint of the active clone).

"rpool/directory" -> root of the ZFS for clones and snapshots.


- Show ZCM information

```bash
$ cd /directory
$ zcm ls
A  ID        MOUNTPOINT  ORIGIN  DATE               
*  00000000  /directory          2021-02-14 04:45:47
```

- Create new clones (derived from active)

```bash
$ cd /directory
$ zcm clone
Created clone 00000001 at path /directory/.clones/00000001
$ zcm clone
Created clone 00000002 at path /directory/.clones/00000002
```

- Activate the previously created clone, mounting it at ZCM path 

```bash
$ zcm -p /directory activate 00000002
Activated clone 00000002
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
$ zcm rm 00000001
```


- Destroy ZCM related data

This is dangerous, you should backup data first.

```bash
$ zcm -p /directory destroy        
WARNING!!!!!!!!
All the filesystems, clones, snapshots and directories associated with /directory will be permanently deleted.
This operation is not reversible.
Do you want to proceed? (yes/NO) yes
Destroyed ZCM at path /directory
```
