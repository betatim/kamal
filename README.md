# kamal

A simple API usage analyser. The goal of this project is to provide a tool that is
very simple to read and understand, in the hope that this increases the chances of
people running it on their private code bases.

## Setup

To analyse source code you need the `kamal.py` script and its only
dependency: `pip install jedi`. Run `python kamal.py --module <module> <path_to_code>`
in an environment that has the `<module>` you are interested in installed.

## Usage

To analyse all the Python files in a folder run:
```
python kamal.py --module <module_name> path/to/python/files
```
This will produce a `statistics.csv` containing one line for each call to a function
or instantiation of a class in `<module_name>`.


## Analysis

A useful tool for exploring the output of kamal is [datasette](https://datasette.io/).

1. Create a sqlite database from the CSV with `sqlite-utils insert --csv statistics.db sklearn statistics.csv`
2. Launch datasette: `datasette serve statistics.db`

To combine the results of multiple `kamal.py` runs can be combined into one database
by running `sqlite-utils insert --csv statistics.db sklearn <CSV>` for each CSV. Each
CSV is appended to the database table.