---
title: Release zoetty
description: Release a new version of zoetty to GitHub, the docs site and PyPI.
output_path: logs/release-<VERSION>.md
inputs:
  - name: VERSION
    description: The version to release, e.g. 0.2.0
    pattern: '^\d+\.\d+\.\d+$'
  - name: UV_PUBLISH_TOKEN
    description: PyPI API token for zoetty
    secret: true
---

# 🎞️ Releasing zoetty

zoetty is released with [paulrun](https://github.com/phalt/paulrun), which runs this runbook:

```sh
uv tool install paulrun
paulrun check PUBLISHING.md
paulrun PUBLISHING.md --dry
paulrun PUBLISHING.md
```

You can also follow it by hand: each step's commands are in the order they run.

Before you start, add a `## <version>` section for the release to the top of
`CHANGELOG.md`, and copy it to `docs/CHANGELOG.md`. That change gets committed
with the version bump.

Each run is recorded in `logs/release-<version>.md`, which git ignores.

## Check before releasing

Releases are made from an up-to-date `main`, with nothing left uncommitted
except the changelog, for a version that hasn't been released yet.

```sh run
git switch main
git pull origin main
git fetch --tags

if [ -n "$(git status --porcelain -- . ':!CHANGELOG.md' ':!docs/CHANGELOG.md' ':!logs')" ]; then
  echo "Commit or stash these changes first:"
  git status --short
  exit 1
fi
if git rev-parse --quiet --verify "refs/tags/<VERSION>" > /dev/null; then
  echo "Tag <VERSION> already exists"
  exit 1
fi
if ! grep -qx "## <VERSION>" CHANGELOG.md; then
  echo "CHANGELOG.md has no '## <VERSION>' section"
  exit 1
fi
```

## Run the checks

The tests have to pass, but coverage isn't checked here: CI holds it at 100% on
Linux, and a few lines only run on Linux, so it reads a little lower on macOS.

```sh run
make ty
make lint-imports
uv run pytest -q
```

## Check the docs clips are up to date

The test suite checks this too, but it's worth seeing before a release.

```sh run
uv run zoetty check docs/clips/*.toml
```

## Update the version

`pyproject.toml` holds zoetty's only copy of its version. `uv version` sets
it and updates `uv.lock` to match.

```sh run
uv version <VERSION>
uv run zoetty --version
```

## Commit and push

There's nothing to commit if the version and changelog were already
committed, e.g. for the first release, or when rerunning one that failed
after this step.

```sh run
if git diff --quiet HEAD; then
  echo "Nothing to commit"
else
  git commit -am "version <VERSION>"
fi
git push origin main
```

## Tag the release

```sh run
git tag <VERSION>
git push origin <VERSION>
```

## Create the GitHub release

These are the release notes, from `CHANGELOG.md`:

```python run
import os
import re
from pathlib import Path

version = re.escape(os.environ["VERSION"])
changelog = Path("CHANGELOG.md").read_text()
notes = re.search(rf"^## {version}\n(.*?)(?=^## |\Z)", changelog, re.MULTILINE | re.DOTALL)
print(notes.group(1).strip())
```

```confirm
Create a release on GitHub from tag <VERSION>:
https://github.com/phalt/zoetty/releases/new?tag=<VERSION>

Paste in the release notes above, and mark it as the latest release.
```

## Publish the documentation

Takes about 5-10 minutes to deploy fully.

```sh run
make deploy-docs
```

## Release to PyPI

`uv publish` uploads everything in `dist/`, so clear it out first.

```sh run
rm -rf dist
# uv publish reads the token from $UV_PUBLISH_TOKEN.
make release
```
