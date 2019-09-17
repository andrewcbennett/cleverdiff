from __future__ import (absolute_import, division, print_function)  # noqa

import sys
import collections

from difflist import DiffList

DiffRecord = collections.namedtuple('DiffRecord',
                                    'diffitem controlindex diffmode')


def contexts(diffitem):
    msg = "{} (line {}) to {} (line {})"
    return msg.format(diffitem.contexts.first, diffitem.lines.first,
                      diffitem.contexts.second, diffitem.lines.second)


def main_diff(file1, file2):
    """
    Given a generator containing diff hunks from difflib, establish the
    similarity of diffs between 
    """
    pass


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
        0: "identical diffs",
        1: "same diff but different lines",
    }

    result = ""
    for seenindex, seenitem, in enumerate(diffseen):
        result += "--------------------------------------------\n"
        result += (f"DIFF {seenindex:3d}:\n"
                   f"{str(seenitem)}")
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


def main(infilepairs):
    diffseen = []
    diffresult = []
    filepairs = [item.split("=") for item in infilepairs]

    for lhs, rhs in filepairs:
        difflist = DiffList.from_files(lhs, rhs)
        for diffitem in difflist.diffs:
            found = False
            if len(diffseen) > 0:
                for seenindex, seenitem, in enumerate(diffseen):
                    cmp = diffitem.compare(seenitem)
                    if cmp < 2:
                        found = True
                        diffresult.append(
                            DiffRecord(
                                diffitem=diffitem,
                                controlindex=seenindex,
                                diffmode=cmp,
                            )
                        )
                        break

            if not found:
                diffseen.append(diffitem)

    print(summarise_results(diffseen, diffresult))


if __name__ == '__main__':
    main(sys.argv[1:])
