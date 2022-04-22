# Suit

Suit is a simple, Pythonic way to handle generic task management for your repository.
It can handle regular repositories fine, but it's in monorepos where the versatility of
this tool shines the most.

## System Requirements

To use Suit on your system, you need:

- Python (>=3.8)
- `pip`

...And that's it.

## Installation Guide

To install Suit on your system, run the following command:

``` sh
> pip install python-suit
```

And that's it. Suit should now be usable on your system.

## Usage Guide

### The root configurations

To use suit, first open a directory in which you'll create your projects.
In that directory, create a file called `suit.toml`:

``` toml
# suit.toml
[suit]
```

Suit actively searches for the `suit.toml` file. It has 2 uses:

1. It's the file where general configurations are set.
2. The location of the file determines the root path of the project.

### Setting scripts

Scripts, unlike our main configurations file, are set in `pyproject.toml` files.
Those `pyproject.toml` files can be set wherever you want, as long as they are within the scope
of the project. The content described in the following, specifically from `root-project-directory`
and inwards will be used in our following examples:

``` text
+ some-other-directory
| - pyproject.toml        # NOT FOUND
| - ...
+ root-project-directory
| - suit.toml
| - pyproject.toml        # FOUND
| - ...
\ + tools
  | - pyproject.toml      # FOUND
  | - my_script.py
```

Inside those `pyproject.toml` files, you can set inline shell scripts to be run. In this example,
I configure the `black` formatter to do linting and formatting on a nearby python script:

``` python
# tools/my_script.py

def main():


    print("Hello World!!")


if __name__ == '__main__':
    main()
```

``` toml
# tools/pyproject.toml

[tool.suit.target.scripts]
prepare-black = "pip install black"
lint = "black --check '{local.path}/my_script.py'"
format = "black '{local.path}/my_script.py'"
```

In the `tools/pyproject.toml` example, 3 scripts are defined:

- `prepare-black` - Installing the `black` Python package.
- `lint` - Running `black --check` on `tools/my_script.py`.
- `format` - Apply the `black` formatter on `tools/my_script.py`.

Now it's time to check out the `suit` CLI.

### The Suit CLI

Suit exposes a console entrypoint, aptly named `suit`.

The relevant commands in our example, are:

- `suit targets` - Will list all of the targets found.
- `suit scripts` - Will list all of the scripts found, alongside the targets defining them.
- `suit run` - Will run the specified scripts of each target (explicitly stated which targets are relevant).

Let's see them in action.

Entering `root-project-directory`, listing the targets and scripts will show the following:

![Listing targets and scripts](/assets/listing_targets_and_scripts_inline.png)

**Explanation**:

- Targets are locations where there's a `pyproject.toml` file with `[tool.suit*]` listed within.
Currently in our example, there's only a single target - The `tools` directory.
- Our only target currently lists 3 scripts, all 3 visible via running the `suit scripts` command.

Let's run stuff, shall we?

``` sh
> suit run prepare-dev format lint
```

This will cause the 3 different scripts to be sequentially executed.
