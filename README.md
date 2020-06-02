# dockered-qbzr
This package provides all the functionalities of [QBzr](https://launchpad.net/qbzr) by using 
[Docker](https://www.docker.com/).

QBzr is a plugin that provides a GUI for Bazaar users. QBzr is based on [Qt4](https://doc.qt.io/archives/qt-4.8/), which is no longer available on the 
newest Ubuntu releases (20.04 and newer).

## Requirements
In order to use this package you will need:
* Linux OS,
* Python 3.6+,
* Docker installation. Please refer to the [installation](https://docs.docker.com/engine/install/ubuntu/) manual.

## Installation
To install the package, simply clone the git repository on your machine:
```bash
git clone https://github.com/akoshakji/dockered-qbzr
```
You can create a symbolic link in /usr/bin for improve the ease of use:
```bash
sudo ln -s /path-to-dockered-qbzr/qbzr.py /usr/local/bin/qbzr
```
or you can create an alias in your .bashrc:
```bash
alias qbzr=/path-to-dockered-qbzr/qbzr.py
```

## Usage
Simply call qbzr command with identical use to the corresponding bzr command, 
as shown in the following examples:
```bash
qbzr qlog
qbzr qcommit file1 dir/file2
qbzr qshelve .
...
```

## Documentation
For more information, you can run `qbzr -h` or `qbzr --help`.

## License
[MIT](https://choosealicense.com/licenses/mit/)
