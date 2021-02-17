# Change log for ZFS Clone Manager

## 2021-XX-XX: Version 3.0.0

- Moved parameter -p,--path as subcommand argument filesystem|path
- Changed subcommand name and aliases behavior 


## 2021-02-17: Version 2.2.0

- Added --auto-remove activate and clone commands
- Unified helper functions in lib module
- Added confirmation message to remove command
- Added --max-total to activate command
- Moved print from Manager to CLI
- Added parseable output to information command


## 2021-02-16: Version 2.1.0

- Added --max-newer and --max-older options to activate command


## 2021-02-16: Version 2.0.0

- Renamed project to ZFS Clone Manager
- Renamed CLI tool to zcm


## 2021-02-15: Version 1.1.0

- Added quiet mode
- Added info command
- Added zfs size info
- Renamed Manager.instances to Manager.clones
- Added older and newer lists
- Added --max-newer and --max-total options to clone command


## 2021-02-15: Version 1.0.0

- First production release


## 2021-02-11: Version 0.0.1

- Start project

