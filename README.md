# Download Biquge Novels

## Introduction

This project is a novel downloader based on Python, which uses the Android APP interface of Biquge for data crawling and
supports multiple functions such as multithreading and asynchronous downloading. It supports batch downloading of novels
through book id, book names, classification serial numbers, local book ids, and also supports epub format downloads.

## Features

The novel downloader mainly implements the following functions:

| Function                                          | Implemented (Y/N) |
|---------------------------------------------------|-------------------|
| Multithreading                                    | Y                 |
| Asynchronous downloading                          | Y                 |
| Command line operation                            | Y                 |
| Downloading by book ID                            | Y                 |
| Downloading by book name                          | Y                 |
| Batch downloading by classification serial number | Y                 |
| Batch downloading by local book ID                | Y                 |
| Support for epub format download                  | Y                 |

Multithreading and asynchronous downloading can greatly improve the speed of novel downloading, and the design of
command line operation also enables users to use this novel downloader conveniently.

## Command Line Usage Help

### Positional Arguments:

* `{download,update,search}`: Available sub-commands
    * `download`: Download a book to a specified directory
    * `update`: Update the book list
    * `search`: Search for a book

### Optional Arguments:

* `-h`, `--help`: Show this help message and exit
* `-e`, `--epub`: Whether or not to generate an epub file

### Usage Examples:

To download a book, use the `download` sub-command along with the `--book-name` and `--output-dir` options:

```
$ python my_app.py download --book-name "book1" --output-dir "/home/user/books"
```

To update the book list, use the `update` sub-command:

```
$ python my_app.py update
```

To search for a book, use the `search` sub-command along with the `--keyword` option:

```
$ python my_app.py search --keyword "python"
```

If you need to generate an epub file, use the `-e` or `--epub` option. For example:

```
$ python my_app.py download --book-name "book1" --output-dir "/home/user/books" --epub
```

You can use the `-h` or `--help` option to see this help message again:

```
$ python my_app.py -h
``` 

## Environment Requirement

To use this novel downloader normally, you need to have the following environment configuration:

- Python 3.6 or above

## Dependencies

To ensure the normal operation of this novel downloader, you also need to install the following dependencies:

- ahttp
- concurrent
- concurrent.futures
- os
- random
- request
- rich
- sys
- time

## Installation of Dependencies

You can install all required dependencies by running the following command:

```sh
pip install -r requirement.txt
```

## Disclaimer

This project is intended for learning and personal use only. It should not be used for any commercial purposes. The
developer of this project is not responsible or liable for any consequences, damages, or losses incurred as a result of
the use of this program for any unauthorized or illegal purpose. The user assumes all responsibility for the use of this
program and agrees to indemnify the developer against any claims or liabilities arising from the use of this program. By
using this program, you agree to these terms and conditions.