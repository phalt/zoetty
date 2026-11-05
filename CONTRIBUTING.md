# Contributing

First things first: thank you for contributing! This project will be successful thanks to everyone who contributes, and we're happy to have you.

## AI disclosure

Within zoetty we use coding agents to prototype and build out ideas, and then take the idea to fruition using human reviewed and approved code.

You, the human and the author of changes are responsible for the contributions, and if you cannot confidently explain or demonstrate understanding of the changes you are contributing, then they will not be accepted.

## Bug or issue?

To raise a bug or issue please use [our GitHub](https://github.com/phalt/zoetty/issues).

Please check the issue has not been raised before by using the search feature.

When submitting an issue or bug, please make sure you provide thorough detail on:

1. The version of zoetty you are using (`zoetty --version`)
2. Your operating system and Python version
3. Any errors or outputs you see in your terminal
4. The smallest clip spec (and capture file, if there is one) that shows the problem. Take out any secrets first!

## Contribution

If you want to directly contribute you can do so in two ways:

1. Documentation
2. Code

### Documentation

We use [mkdocs](https://www.mkdocs.org/) and [GitHub pages](https://pages.github.com/) to deploy our docs.

Fixing grammar, spelling mistakes, or expanding the documentation to cover features that are not yet documented, are all valuable contributions.

Please see the **Set up** instructions below to run the docs locally on your computer, then:

```sh
make docs-serve
```

The examples in the docs and the README are tested, so if you change one, run `make test` too.

### Code

Contribution by writing code for new features, or fixing bugs, is a great way to contribute to the project.

Please [open an issue](https://github.com/phalt/zoetty/issues) to talk it through before changing the clip spec format (keys, markup or what `record` does), adding a command or flag, adding JavaScript to an output, or adding a dependency. These are hard to change once people's clips rely on them.

#### Set up

Clone the repo:

```sh
git clone git@github.com:phalt/zoetty.git
cd zoetty
```

Move to a feature branch:

```sh
git switch -c my-branch-name
```

Install UV (if not already installed):

```sh
# On macOS and Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip:
pip install uv
```

Install all the dependencies:

```sh
make install
```

This will use UV to create a virtual environment and install all dependencies, including zoetty itself. UV handles the virtual environment automatically, so you don't need to manually activate it.

To make sure you have things set up correctly, please run the tests:

```sh
make test
```

You can run your copy of zoetty with `uv run zoetty`, e.g. to rebuild the docs clips:

```sh
uv run zoetty build docs/clips/*.toml
```

Run `make help` to see every command.

### Preparing changes for review

Once you've made changes, here's a good checklist to run through before publishing for review:

Format and lint the code:

```sh
make format
```

Check the types:

```sh
make ty
```

Check the import contracts:

```sh
make lint-imports
```

[Import Linter](https://import-linter.readthedocs.io/) checks that modules only import in the directions we want: `zoetty.cli` sits on top and wires everything together, the renderers never import each other or the recorder, and only the CLI uses `click` and `rich`. The contracts, and the reasons for them, are under `[tool.importlinter]` in `pyproject.toml`. If one breaks, change the import rather than the contract.

Run the tests:

```sh
make test
```

New behaviour needs tests, and coverage stays at 100%. A new spec feature also gets an example in `docs/clips/` and on `docs/examples.md`.

If you've changed how clips are written or built, update `docs/clip-format.md` or `docs/cli.md` to match. If a change alters what zoetty draws, rebuild the docs clips with `uv run zoetty build docs/clips/*.toml`; a test fails if they're stale.

Make sure you add to `CHANGELOG.md` and `docs/CHANGELOG.md` what changes you have made. The two must be identical, and a test checks they are.

Make sure you add your name to `CONTRIBUTORS.md` as well!

### Making a pull request

Please push your changes up to a feature branch and make a new [pull request](https://github.com/phalt/zoetty/compare) on GitHub.

Please add a description to the PR and some information about why the change is being made.

After a review, you might need to make more changes.

Once accepted, a core contributor will merge your changes!
