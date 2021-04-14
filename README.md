[![latest release](https://img.shields.io/pypi/v/cleverdiff?color=blue&label=latest%20release)](https://pypi.org/project/cleverdiff/)
[![license](https://img.shields.io/github/license/andrewcbennett/cleverdiff?color=yellow)](https://github.com/andrewcbennett/cleverdiff/blob/main/LICENSE)

[![test status](https://img.shields.io/github/workflow/status/andrewcbennett/cleverdiff/test/main?label=tests)](https://github.com/andrewcbennett/cleverdiff/actions/workflows/test.yml)
[![security test status](https://img.shields.io/github/workflow/status/andrewcbennett/cleverdiff/codeql-analysis/security-workflow?label=security)](https://github.com/andrewcbennett/cleverdiff/security)

[![contributors](https://img.shields.io/github/contributors/andrewcbennett/cleverdiff)](https://github.com/andrewcbennett/cleverdiff/graphs/contributors)
[![open issues](https://img.shields.io/github/issues-raw/andrewcbennett/cleverdiff)](https://github.com/andrewcbennett/cleverdiff/issues?q=is:open+is:issue)
[![issues for beginners](https://img.shields.io/github/issues-raw/andrewcbennett/cleverdiff/good%20first%20issue?color=dark+green&label=issues+for+beginners)](https://github.com/andrewcbennett/cleverdiff/issues?q=is%3Aopen+is:issue+label:"good+first+issue")

# CleverDiff
A command-line tool for succinctly describing multiple differences in files.

## Why?
If you have to compare files which contain multiple differences that are the same, you will know how tedious it is to step through every single hunk of the standard `diff` output. *CleverDiff* will show you each unique diff hunk once, then give you a summary of where else it has found the difference across multiple files.

## Installation
*CleverDiff* is available on PyPI:
```
pip install --user cleverdiff
```

## Usage
Run the `cleverdiff.py` script, with each pair of files separated with `=` as arguments:
```
python3 cleverdiff.py test_data/ref1.def=test_data/new1.def test_data/ref2.def=test_data/new2.def
```

Or run the cleverdiff.py script, with --old followed by a list of reference files and --new followed by a list of modified files:

```console
python3 cleverdiff.py --old test_data/ref.def test_data/ref2.def \
                      --new test_data/new.def test_data/new2.def
```

*CleverDiff* will find the differences between each pair of files, then determine which are identical across all files, and give you a summary:

```
--------------------------------------------
DIFF   0:
insert in ref.def:49 vs new.def:50:
+        edit FOO bar

This difference is replicated elsewhere:
 * with identical diff in different files:
    ref2.def:49 vs new2.def:50


--------------------------------------------
DIFF   1:
change in ref.def:339 vs new.def:340:
-              family sat_172
-                edit WMOID '172'
+              family sat_173
+                edit WMOID '173'

This difference is replicated elsewhere:
 * with identical diff in different files:
    ref2.def:339 vs new2.def:340
 * with same diff but different line numbers:
    ref.def:376 vs new.def:377
    ref.def:413 vs new.def:414
    ref.def:450 vs new.def:451
    ref.def:487 vs new.def:488
    ref2.def:376 vs new2.def:377
    ref2.def:413 vs new2.def:414
    ref2.def:450 vs new2.def:451
    ref2.def:487 vs new2.def:488
```

## Version history

### v0.3
Contributors: @vhsw
* Add command-line arguments `--old` and `--new` (#7)
* Add black, isort & pyflakes to CI tests (#4)

### v0.2
Contributors: @andrewcbennett
Introduces ecFlow context (#2). Bug fixes.

### v0.1.2
Contributors: @andrewcbennett (with thanks to @takluyver)
Fixes failing tests. Adds Travis CI config.

### v0.1
Contributors: @andrewcbennett (with thanks to @takluyver)
initial version
