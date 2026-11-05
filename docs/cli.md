# 📟 Command line

Every command takes one or more spec files, so a shell glob does a whole folder: `zoetty build docs/clips/*.toml`.

## `zoetty init SPEC`

Writes a starter spec to `SPEC`, which builds as it is. It won't overwrite a file that already exists.

```sh
zoetty init docs/clips/hello.toml
```

## `zoetty record SPEC...`

For each spec: runs its `[record] setup` commands, then every run that has an `output` file (and isn't `record = false`), in order, in a pseudo-terminal the size of the clip. What each command prints is saved to its `output` file.

```sh
zoetty record docs/clips/start-api.toml
```

```text
docs/clips/start-api.toml
  ✓ clientele start-api -f schema.json -o my_client/ · exit 0 → docs/clips/captures/start-api.ansi
  ✓ ls my_client/ · exit 0 → docs/clips/captures/ls.ansi
```

A command that exits non-zero is marked `!` and still recorded. A failing setup command or a timeout stops that clip and makes `record` exit 1.

Runs with `lines` are never executed, so `record` is safe to run on every clip.

## `zoetty build SPEC...`

Renders each spec to its `out` files.

```sh
zoetty build docs/clips/*.toml
```

```text
✓ docs/clips/hello.svg (4.3KB)
✓ docs/clips/hello.html (4.0KB)
```

If a spec is broken, or a run's `output` hasn't been recorded yet, `build` says so, carries on with the others, and exits 1.

## `zoetty check SPEC...`

Checks each spec is valid and that every one of its `out` files exists and matches a fresh build. Nothing is written. Exits 1 if anything is wrong, so it's made for CI:

```sh
zoetty check docs/clips/*.toml
```

```text
✓ docs/clips/hello.toml
✗ docs/clips/zen.svg is out of date: run zoetty build docs/clips/zen.toml
```

`check` doesn't re-record anything: it trusts the captures in your repo. It only needs zoetty installed, not the tools your clips show.

## `zoetty --version`

Prints the version.
