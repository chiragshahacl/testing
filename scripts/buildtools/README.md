# Buildtools

# CLI

**Usage**:

```console
$ [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `get-projects`
* `ignore`

## `get-projects`

* `output-location`: Where to place generated output file
* `previous-commit`: Commit to base commit of
* `current-commit`: Commit to compare with base commit
* `category`: Filter by project category
* `deployable`: Filter by deployables projects
* `no-deployable`: Filter by non deployable projects


**Usage**:

```console
$ get-projects [OPTIONS] OUTPUT_LOCATION
```

**Arguments**:

* `OUTPUT_LOCATION`: [required]

**Options**:

* `--previous-commit TEXT`
* `--current-commit TEXT`
* `--category TEXT`
* `--deployable / --no-deployable`
* `--help`: Show this message and exit.

## `ignore`

**Usage**:

```console
$ ignore [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
