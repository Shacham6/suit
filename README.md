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

Installing Suit is just a `pip install` away!

``` sh
> pip install python-suit
```

## Usage Guide

### The root configurations

Using Suit first requires a file named `suit.toml` at the root of your repository.

``` toml
# suit.toml
[suit]
```

Suit actively searches for the `suit.toml` file. Without that file, the program won't work.
The `suit.toml` file has 2 uses:

1. It's the file where general configurations are set.
2. The location of the file determines the root path of the project.

### Target Scripts - Inlined

You can configure scripts by adding scripts in a `[tool.suit.target.scripts]` section in
`pyproject.toml` files.

``` toml
[tool.suit.target.scripts]
hello = 'echo "Hello"'
world = 'echo " world"'
but-with-energy = 'echo "!"'
```

You can run each individually by running

``` sh
> suit run hello world but-with-shouting
```

But you can also bundle multiple commands together by creating compounding-scripts.

``` toml
[tool.suit.target.scripts]
hello = 'echo "Hello"'
world = 'echo " world"'
but-with-energy = 'echo "!"'

hello-world = [
  {ref = 'hello'},
  {ref = 'world'},
  {ref = 'but-with-energy'},
]
```

And then the compound script.

``` sh
> suit run hello-world
```

### Target Scripts - Inheritance

Settings scripts inside targets is fine, but in monorepos we expect a lot of those scripts
to repeat themselves.

That's why Suit offers a templating solution for targets!

Creating a template means adding a `[suit.templates.XXX]` table in the `suit.toml` file, where `XXX` is the designated template name.

The following is an example for a template named `helloer`, which provides the scripts from the
previous example.

``` toml
# suit.toml
[suit.templates.helloer.scripts]

hello = 'echo "Hello"'
world = 'echo "world"'
but-with-shouting = 'echo "!!"'

hello-world = [
    {ref = 'hello'},
    {ref = 'world'},
    {ref = 'but-with-shouting'}
]
```

And in the `pyproject.toml` the previously held those scripts, the following can now be put:

``` toml
# pyproject.toml
[tool.suit.target]
inherit = ['helloer']
```

## Roadmap

Suit is not close to be done. There are plenty of great ideas in where this project will go.

Among the best ones:

- Configurable `virtualenv`s management.
- `pre-commit-hooks` integration.
- Parallelization
