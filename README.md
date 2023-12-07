MADS CLI
========

### Master of Applied Data Science Command Line Interface

We use the command line for many different operations in different environments
across the program. These different use cases share some common features, like
loading config files; detecting the runtime environment; interacting with
Docker, GitHub, Kubernetes; and streaming the output of shell commands among
others.

This library is a foundation from which to build the other solutions. It
implements a single command line tool and loads application-specific plugins
using the python
[entry point system](https://packaging.python.org/en/latest/specifications/entry-points/).


## End-User Usage

With no plugins installed, running `mads` presents this usage output:

```
usage: mads [-h] {docker,github,kube,setup} ...

MADS commands

options:
  -h, --help            show this help message and exit

Commands:
  {docker,github,kube,setup}
                        Available commands
    docker              Helpers for interacting with Docker
    github              Helpers for interacting with GitHub
    kube                Helpers for interacting with Kubernetes
    setup               Helpers for setting up a build environment

This tool lives at https://github.com/umsi-mads/mads-cli
```


## Developer Usage

In order to add a plugin, you need to publish a module with a few attributes:


### An Entry Point

Your python package should include an entry point in your setup metadata. For
example,

```toml
# pyproject.toml
[project.entry-points."mads-cli"]
fizz = "mypackage.fizzbuzz"
```

The subcommand will use the entrypoint name, in this case `fizz`.

### The Module

The module and its metadata is used to set up your subcommand.

The "help" description of the subcommand is either `mod.__doc__` or `mod.help`.


### The Register Function

The module also needs to include a function, which may look like the following:

```python
# fizzbuzz.py
"""Print the Fizzbuzz sequence up to a given number"""

import argparse
from mads.cli.command import command


def register_subcommand(parser: argparse.ArgumentParser):
    """Register the fizzbuzz command"""

    fbcmd = parser.add_subparsers(title="Fizzbuzz commands", help="Available commands")

    @command(fbcmd)
    def run(upto: int, fizz: int = 3, buzz: int = 5):
        """Run Fizzbuzz with custom numbers"""

        for i in range(1, upto + 1):
            if i % fizz == 0:
                print("fizz", end="")
            if i % buzz == 0:
                print("buzz", end="")
            if i % fizz != 0 and i % buzz != 0:
                print(i, end="")
            print("")
```

This code will install the `fizz` subcommand with a usage doc that looks
like the following:

```
usage: mads fizz [-h] {run} ...

options:
  -h, --help  show this help message and exit

Fizzbuzz commands:
  {run}       Available commands
    run       Run Fizzbuzz with custom numbers
```
