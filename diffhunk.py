from __future__ import (absolute_import, division, print_function)  # noqa

import collections


class DiffHunk(object):
    """A class to contain a single difference between two strings."""

    def __init__(self, mode, content, lines):
        """
        Initialise a DiffHunk object.

        Arguments
        ---------

        mode : str
            Describes the action - one of `"change"`, `"insert"`, or
            `"delete"`.

        content : str
            The actual content of the difference in each file.

        lines : Pair
            The starting line numbers of the difference on each side as
            integers.

        """
        self.mode = mode
        self.content = content
        self.lines = lines

    def context_to_string(self):
        return f"line {self.lines.first} vs line {self.lines.second}"

    def __str__(self):
        return f"{self.mode} in {self.context_to_string()}:\n{self.content}\n"

    def compare(self, other):
        """
        Compares this diff hunk with another, and returns the nature of the
        differences.

        Arguments
        ---------
        other : DiffHunk
            The diff hunk object with which to compare.

        Returns
        -------
        int
            The nature of the differences:
                0 = no differences (the hunks are identical)
                1 = line numbers differ only
                2 = all parts of the hunks differ
        """
        if self.content != other.content or self.mode != other.mode:
            return 2
        elif self.lines != other.lines:
            return 1
        return 0


Pair = collections.namedtuple("Pair", "first second")
