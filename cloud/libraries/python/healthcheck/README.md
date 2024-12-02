# healthcheck library

TODO: Write description

# 📔 Documentation
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
- Run feature tests
- Run unit test

There are also a couple of scripts for formatting the code with black and running feature tests independently.
