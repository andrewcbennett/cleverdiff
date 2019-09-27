from __future__ import absolute_import, division, print_function  # noqa

import sys
import os.path
import collections
import argparse

from .difflist import DiffList
from .contexts import DefaultContext, lookup_extension

DiffRecord = collections.namedtuple("DiffRecord", "diffitem controlindex diffmode")


def summarise_results(diffseen, diffresult):
    """
    Given a list of difference records, creates a human-readable summary of
    the differences.

    Arguments
    ---------
    diffseen : list of `difflist.DiffHunk`
        A list of differences that have not been seen before.

    diffresult : list of DiffRecord
        A list of differences to summarise.

    Returns
    -------
    str
        A string containing human-readable text which contains a
        summary of the contents of diffresult.
    """
    MODE_DESCRIPTION = {
        0: "identical diff in different files",
        1: "same diff but different line numbers",
    }

    result = ""
    for seenindex, seenitem in enumerate(diffseen):
        result += "--------------------------------------------\n"
        result += f"DIFF {seenindex:3d}:\n" f"{str(seenitem)}"
        result2 = {key: [] for key in MODE_DESCRIPTION.keys()}
        for hunk2, controlindex, mode in diffresult:
            if controlindex != seenindex:
                continue

            # TODO: stick this assert in a test!
            assert mode < 2, "unexpected value for mode"
            result2[mode].append(hunk2)

        if any([len(v) for v in result2.values()]):
            result += f"This difference is replicated elsewhere:\n"
            for mode, diffitems in result2.items():
                if diffitems:
                    result += f" * with {MODE_DESCRIPTION[mode]}:\n"
                    for diffitem in diffitems:
                        result += f"    {diffitem.context_to_string()}\n"
            result += "\n\n"

    return result


def main_diff(filepairs, context_cls=None):
    diffseen = []
    diffresult = []

    for lhs, rhs in filepairs:
        difflist = DiffList.from_files(lhs, rhs, context_cls)
        for diffitem in difflist.diffs:
            found = False
            if len(diffseen) > 0:
                for seenindex, seenitem in enumerate(diffseen):
                    cmp = diffitem.compare(seenitem)
                    if cmp < 2:
                        found = True
                        diffresult.append(
                            DiffRecord(
                                diffitem=diffitem, controlindex=seenindex, diffmode=cmp
                            )
                        )
                        break

            if not found:
                diffseen.append(diffitem)

    print(summarise_results(diffseen, diffresult))


def main():
    parser = argparse.ArgumentParser(
        prog="cleverdiff",
        description="A tool for describing multiple differences in files",
    )
    pairs = parser.add_argument_group("list of file pairs")

    def file_pair(string):
        pair = string.split("=")
        if len(pair) != 2 or "" in pair:
            raise ValueError
        return pair

    pairs.add_argument(
        "files_pairs",
        metavar="file1=file2",
        type=file_pair,
        nargs="*",
        help="pair of files separated with '='",
    )
    old_new = parser.add_argument_group("or separately")
    old_new.add_argument(
        "--old",
        dest="old_files",
        default=[],
        metavar="file",
        type=str,
        nargs="*",
        help="list of reference files",
    )
    old_new.add_argument(
        "--new",
        dest="new_files",
        default=[],
        metavar="file",
        type=str,
        nargs="*",
        help="list of modified files",
    )
    args = parser.parse_args()
    if not args.old_files and not args.new_files and not args.files_pairs:
        raise ValueError("No files specified")
    if len(args.old_files) != len(args.new_files):
        raise ValueError("The number of reference and modified files must be equal")
    file_pairs = args.files_pairs
    file_pairs += list(zip(args.old_files, args.new_files))
    exts = [os.path.splitext(f)[-1] for file_pair in file_pairs for f in file_pair]
    if len(set(exts)) > 1:
        context_cls = DefaultContext
    else:
        context_cls = lookup_extension(exts[0])

    print(f"detected {context_cls.DESCRIPTION}")
    main_diff(file_pairs, context_cls=context_cls)
