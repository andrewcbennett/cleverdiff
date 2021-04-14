from __future__ import absolute_import, division, print_function  # noqa

import difflib

from cleverdiff.contexts import DefaultContext
from cleverdiff.diffhunk import DiffHunk, Pair


class DiffList(object):
    """A class to contain lists of differences between two strings."""

    def __init__(self, string1, string2, label1="", label2="", context_objects=None):
        """Initialise a DiffList object."""

        super(DiffList, self).__init__()

        # Initialise attributes.
        self._first = string1.splitlines(True)
        self._second = string2.splitlines(True)
        self._firstlabel = label1
        self._secondlabel = label2

        # Initialise objects to manage context.
        if context_objects is None:
            self._firstcontext = DefaultContext(label1)
            self._secondcontext = DefaultContext(label2)
        else:
            self._firstcontext, self._secondcontext = context_objects

        # Compute and parse differences.
        self._diffs = self._parse(difflib.unified_diff(self._first, self._second, n=0))

    @classmethod
    def _translate_diff_syntax(cls, syntax):
        """
        Turns unified diff syntax of into a more useful form.

        Arguments
        ---------
        syntax: str
            The input unified diff syntax to translate. Must be in the form:
            "@@ -n1,n2 +m1,m2 @@" as described in
            https://www.gnu.org/software/diffutils/manual/html_node/Detailed-Unified.html#Detailed-Unified

        Returns
        -------
        tuple of (str, int, int)
            The result of parsing. The str is: "insert", "delete" or "change",
            and the two integers are the start line from each input.
        """
        import re

        pattern = re.compile(r"^@@ -(\d+)(,(\d*))? \+(\d+)(,(\d*))? @@$")
        result = pattern.match(syntax)
        try:
            start1, _, length1, start2, _, length2 = result.groups()
            start1 = int(start1)
            start2 = int(start2)
        except (AttributeError, TypeError):
            msg = "malformed unified diff hunk syntax: {}"
            raise ValueError(msg.format(syntax))

        try:
            length1 = int(length1)
        except TypeError:
            length1 = 1

        try:
            length2 = int(length2)
        except TypeError:
            length2 = 1

        if length1 == 0:
            mode = "insert"
        elif length2 == 0:
            mode = "delete"
        else:
            mode = "change"

        return mode, start1, start2

    @classmethod
    def from_files(cls, file1, file2, context_cls=None):
        """
        Construct a DiffList object from the differences between two
        files.

        Arguments
        ---------
        file1 : str
            The filename of the first file.

        file2 : str
            The filename of the second file.

        context_cls : type, optional
            A class which will be instantiated for each of the filenames
            above, and will provide the human-readable context of lines.
            If not provided, defaults to DefaultContext.

        Returns
        -------
        DiffList
            An object representing the differences between the given files.
        """
        if context_cls is None:
            context_cls = DefaultContext

        try:
            with open(file1, "rt") as f1, open(file2, "rt") as f2:
                return cls(
                    f1.read(),
                    f2.read(),
                    label1=file1,
                    label2=file2,
                    context_objects=[context_cls(file1), context_cls(file2)],
                )
        except IOError as excinfo:
            msg = "failed to load from file {}: {}"
            raise IOError(msg.format(excinfo.filename, excinfo))

    def _parse(self, input_lines):
        """
        Parses a string and translates it into a list of DiffHunk objects.

        Arguments
        ---------
        input_lines : list of str
            A list of strings containing a sequence of differences to parse.
            Must be in GNU unified diff format, defined at:
            https://www.gnu.org/software/diffutils/manual/html_node/Detailed-Unified.html#Detailed-Unified

        Returns
        -------
        list
            A list of DiffHunk objects.

        """
        difflist = []
        hunk_content = ""
        mode = ""
        line1 = line2 = 0
        for diff_line in input_lines:
            if diff_line.startswith("---"):
                continue
            elif diff_line.startswith("+++"):
                continue
            elif diff_line.startswith("@@"):
                if mode:
                    hunk_obj = DiffHunk(
                        mode=mode,
                        content=hunk_content,
                        context=Pair(
                            first=self._firstcontext[line1],
                            second=self._secondcontext[line2],
                        ),
                        lines=Pair(first=line1, second=line2),
                    )
                    difflist.append(hunk_obj)

                # next hunk...
                mode, line1, line2 = self._translate_diff_syntax(diff_line)
                hunk_content = ""
            else:
                hunk_content += diff_line

        hunk_obj = DiffHunk(
            mode=mode,
            content=hunk_content,
            context=Pair(
                first=self._firstcontext[line1], second=self._secondcontext[line2]
            ),
            lines=Pair(first=line1, second=line2),
        )
        difflist.append(hunk_obj)

        return difflist

    @property
    def diffs(self):
        """The list of differences as DiffHunk objects."""
        return self._diffs
