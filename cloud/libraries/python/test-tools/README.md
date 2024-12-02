# Test Tools Library 🔬🧪

Library containing tools used during testing for our apps.

# 📔 Documentation

## Asserts
### Data Comparison Functions

```Python
assert_deep_equal(actual, expected, sort_keys=True)
```

This function is used to compare two data structures deeply and raise an assertion error if the data structures are not equal, 
prints a human-readable message and a diff table to help with debugging.

Supports a variety of data types, including dicts, lists, strings, and numbers.

If sort_keys is True, the keys of the actual and expected dictionaries will be sorted before comparison.

```Python
assert_contains(actual, expected)
```

The assert_deep_contains function compares two dicts deeply and raises an assertion error if the actual dict does not contain all of the keys and values of the expected dict.
The function also checks for nested dicts and recursively compares the values of the two dicts.

#### Diff Table
If the data structures are not equal, the functions will print a diff table to help with debugging. 
The diff table shows the differences between the two data structures in a human-readable format.


# 💻 Running

## Installation
To install the project locally, the easiest way is to run the build script located in the project root directory
(Please check the script prerequisites in the next section if this is your first time running the project).

The build script takes care of installing all the project dependencies, running tests, performing code validation,
and running linters.

```shell
./build.sh
```

 _**Note**: Please note that the build script generates a `.env` file in the root folder, which contains the necessary environment
variables for running the project. While these variables have default values set, some of them may need to be updated to 
reflect your local environment. Therefore, it is recommended that you check the `.env` file and modify the relevant 
variables as needed before running the project._

# ⚙️ Requirements

## Python

If Python is not installed I recommend installing manually from Python's [website](https://www.python.org/downloads/).
Check `pyproject.toml` for exact Python version.

## Install Poetry

You can follow the steps at Poetry's [doc](https://python-poetry.org/docs/), or install by using:

```shell
curl -sSL https://install.python-poetry.org | python3 -
```

# 🧰 Scripts

The scripts assume the project requirements are installed and running.

We have a main build script which will:

- Install dependencies
- Format code
- Run unit test

There are also a couple of scripts for formatting the code with black and running feature tests independently.
