# Change log for ZFS Clone Manager


## 2021-02-23: Version 3.3.0

- Changed zfs_set(zfs_name,mounted=*) to zfs_[un]mount(zfs_name)
- Fix zfs not mounted after migration
- Changed shutil.copytree and shutil.copy2 to "cd source; tar cf - . | (cd target; tar xf -)" command
- Fixed "option not recongnized" bug in zfs/get_cmd()
- Library zfs* functions now raise ZFSError on error and returns stdout instead of returncode
- Added JSON output to commands clone and list


## 2021-02-22: Version 3.2.1

- Fix some copy paste issues with some strings


## 2021-02-22: Version 3.2.0

- Added new check in Manager.load()
- Added command diff
- Added pagination to print_table (and print commands)
- Added supress headers to print_table (and print commands)
- Added parameter to initialize command with migration
- Renamed Manager.initialize_zfs() to Manager.initialize_manager()


## 2021-02-21: Version 3.1.0

- Fix Manager.size uninitialized
- Removed loop for path detection in get_zcm_for_path()
- Removed ZFS property zfs_clone_manager:active.
  Active detection going back to clone_zfs.mountpoint==root_zfs.zfs_clone_manager:path
- Renamed back create command to clone


## 2021-02-20: Version 3.0.0

- Moved parameter -p,--path as subcommand argument filesystem|path
- Changed subcommand name and aliases behavior 
- Added zfs_clone_manager:path and zfs_clone_manager:active ZFS properties handling
- Renamed zfs property to name in Manager
- Better handling of on/off properties in zfs
- Added Clone class to use it instead of a dict
- Renamed name properties to zfs in Manager and Clone


## 2021-02-17: Version 2.2.0

- Added --auto-remove activate and clone commands
- Unified helper functions in lib module
- Added confirmation message to remove command
- Added --max-total to activate command
- Moved print from Manager to CLI
- Added parseable output to information command
- Added Clone class for use instead of dict
- Renamed instance properties to clone in Manager


## 2021-02-16: Version 2.1.0

- Added --max-newer and --max-older options to activate command


## 2021-02-16: Version 2.0.0

- Renamed project to ZFS Clone Manager
- Renamed CLI tool to zcm


## 2021-02-15: Version 1.1.0

- Added quiet mode
- Added info command
- Added zfs size info
- Renamed Manager.clones to Manager.clones
- Added older and newer lists
- Added --max-newer and --max-total options to clone command


## 2021-02-15: Version 1.0.0

- First production release


## 2021-02-11: Version 0.0.1

- Start project

