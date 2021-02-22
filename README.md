# ZFS Clone Manager

Tool to add version control and historic data of a directory with ZFS. The functionality is similar to Solaris beadm but generalized for any ZFS filesystem, not just ROOT and VAR.

The suggested workflow is:
1. Initialize a manager (zcm init)
2. Make changes in active clone
3. Create new clone (zcm clone)
4. Make changes in new clone
5. Activate new clone (zcm activate)
6. [Remove older clones (zcm rm)]
7. Go to step 2

## Usage

- Initialize a ZCM manager

    ```bash
    $ zcm init rpool/directory /directory
    ZCM initialized ZFS rpool/directory at path /directory
    ```

    "rpool/directory" -> root of the ZFS for clones and snapshots.
    "/directory" -> path of the filesystem (mountpoint of the active clone).


- Show ZCM information

    ```bash
    $ zcm info /directory
    Path: /directory
    Root ZFS: rpool/directory
    Root ZFS size: 63.00 KB
    Total clone count: 1
    Older clone count: 0
    Newer clone count: 0
    Oldest clone ID: 00000000
    Active clone ID: 00000000
    Newest clone ID: 00000000
    Next clone ID: 00000001

    $ zcm ls /directory
    MANAGER          A  ID        CLONE                     MOUNTPOINT  ORIGIN    DATE                 SIZE    
    rpool/directory     00000001  rpool/directory/00000000  /directory            2021-02-16 10:46:59  32.00 KB
    ```

- Create new clones (derived from active)

    ```bash
    $ zcm clone /directory
    Created clone 00000001 at path /directory/.clones/00000001
    $ zcm clone /directory
    Created clone 00000002 at path /directory/.clones/00000002
    $ zcm ls /directory
    MANAGER          A  ID        CLONE                     MOUNTPOINT                   ORIGIN    DATE                 SIZE    
    rpool/directory  *  00000000  rpool/directory/00000000  /directory                             2021-02-20 06:51:14  32.00 KB
    rpool/directory     00000001  rpool/directory/00000001  /directory/.clones/00000001  00000000  2021-02-20 06:57:01  18.00 KB
    rpool/directory     00000002  rpool/directory/00000002  /directory/.clones/00000002  00000000  2021-02-20 06:57:02  18.00 KB
    ```

- Activate the previously created clone, mounting it at ZCM path 

    ```bash
    $ zcm activate /directory 00000002
    Activated clone 00000002
    ```

    The activate command can not be executed from inside the path, therefore the parameter -p <path> is mandatory.  

- All the clones are visible at <path>/.clones

    ```bash
    $ ls /directory/.clones
    0000000 00000001 00000002
    ```


- Show differences of a clone from it's origin

    ```bash
    $ mkdir /directory/tmp
    $ mkfile 10m /directory/tmp/file
    $ zcm diff /directory
    MOUNTPOINT  DATE                        CHANGE    FILE      FILE_TYPE
    /directory  2021-02-22 06:19:34.094470  Modified  .         directory
    /directory  2021-02-22 06:21:07.236145  Added     tmp       directory
    /directory  2021-02-22 06:21:07.309059  Added     tmp/file  file     
    ```


- Remove clones

    ```bash
    $ zcm rm /directory 00000001
    WARNING!!!!!!!!
    All the filesystems, snapshots and directories associated with clone 00000001 will be permanently deleted.
    This operation is not reversible.
    Do you want to proceed? (yes/NO) yes
    Removed clone 00000001
    ```


- Destroy ZCM related data

    This is dangerous, you should backup data first.

    ```bash
    $ zcm destroy /directory
    WARNING!!!!!!!!
    All the filesystems, clones, snapshots and directories associated with rpool/directory will be permanently deleted.
    This operation is not reversible.
    Do you want to proceed? (yes/NO) yes
    Destroyed ZCM rpool/directory
    ```


- Initialize a ZCM manager based on an existing directory:

    ```bash
    $ zcm ls /directory
    There is no ZCM manager at /directory
    $ mkdir -p /directory/tmp
    $ mkfile 10m /directory/tmp/file
    $ zcm init -M rpool/directory /directory
    ZCM initialized ZFS rpool/directory at path /directory
    $ zcm ls rpool/directory
    MANAGER          A  ID        CLONE                     MOUNTPOINT  ORIGIN  DATE                 SIZE    
    rpool/directory  *  00000000  rpool/directory/00000000  /directory          2021-02-22 13:37:28  10.04 MB
    $ ls /directory
    .clones/ tmp/     
    $ ls /directory/tmp
    file
    ```


- Initialize a ZCM manager based on an existing ZFS:


    ```bash
    $ zfs create -o mountpoint=/directory rpool/directory
    $ mkdir /directory/tmp
    $ mkfile 10m /directory/tmp/file
    $ zcm init -m rpool/directory /directory
    ZCM initialized ZFS rpool/directory at path /directory
    $ zcm ls rpool/directory
    MANAGER          A  ID        CLONE                     MOUNTPOINT  ORIGIN  DATE                 SIZE    
    rpool/directory  *  00000000  rpool/directory/00000000  /directory          2021-02-22 13:39:43  10.04 MB
    $ ls /directory 
    tmp
    $ ls /directory/tmp
    file
    ```