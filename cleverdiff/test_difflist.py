from __future__ import absolute_import, division, print_function  # noqa

import difflib
import os
import tempfile
import textwrap

import pytest
from mock import call, patch

from cleverdiff.diffhunk import Pair
from cleverdiff.difflist import DiffList


class Test_DiffList__translate_diff_syntax(object):
    def test_insert_one(self):
        ref = textwrap.dedent(
            """\
                    line1
                    line2
                """
        ).splitlines()
        new = textwrap.dedent(
            """\
                    line1
                    insert
                    line2
                """
        ).splitlines()
        syntax, = [
            i.strip() for i in difflib.unified_diff(ref, new, n=0) if i.startswith("@@")
        ]

        # unified diff hunk format:
        # @@ -start,count +start,count @@
        # -start and +start are starting line numbers in first and second file
        # count is omitted if 1
        # see https://www.gnu.org/software/diffutils/manual/html_node/Detailed-Unified.html#Detailed-Unified
        assert syntax == "@@ -1,0 +2 @@"
        expected = ("insert", 1, 2)  # "i",start1,start2
        actual = DiffList._translate_diff_syntax(syntax)
        assert actual == expected

    def test_insert_many(self):
        ref = textwrap.dedent(
            """\
                    line1
                    line4
                """
        ).splitlines()
        new = textwrap.dedent(
            """\
                    line1
                    line2
                    line3
                    line4
                """
        ).splitlines()
        syntax, = [
            i.strip() for i in difflib.unified_diff(ref, new, n=0) if i.startswith("@@")
        ]
        assert syntax == "@@ -1,0 +2,2 @@"
        expected = ("insert", 1, 2)
        actual = DiffList._translate_diff_syntax(syntax)
        assert actual == expected

    def test_delete_one(self):
        ref = textwrap.dedent(
            """\
                    line1
                    deleteme
                    line2
                """
        ).splitlines()
        new = textwrap.dedent(
            """\
                    line1
                    line2
                """
        ).splitlines()
        syntax, = [
            i.strip() for i in difflib.unified_diff(ref, new, n=0) if i.startswith("@@")
        ]
        assert syntax == "@@ -2 +1,0 @@"
        expected = ("delete", 2, 1)  # "d",start1,start2
        actual = DiffList._translate_diff_syntax(syntax)
        assert actual == expected

    def test_delete_many(self):
        ref = textwrap.dedent(
            """\
                    line1
                    deleteme
                    deletemetoo
                    line2
                """
        ).splitlines()
        new = textwrap.dedent(
            """\
                    line1
                    line2
                """
        ).splitlines()
        syntax, = [
            i.strip() for i in difflib.unified_diff(ref, new, n=0) if i.startswith("@@")
        ]
        assert syntax == "@@ -2,2 +1,0 @@"
        expected = ("delete", 2, 1)
        actual = DiffList._translate_diff_syntax(syntax)
        assert actual == expected

    def test_change_one(self):
        ref = textwrap.dedent(
            """\
                    line1
                    oldline
                    line2
                """
        ).splitlines()
        new = textwrap.dedent(
            """\
                    line1
                    newline
                    line2
                """
        ).splitlines()
        syntax, = [
            i.strip() for i in difflib.unified_diff(ref, new, n=0) if i.startswith("@@")
        ]
        assert syntax == "@@ -2 +2 @@"
        expected = ("change", 2, 2)  # "c",start1,start2
        actual = DiffList._translate_diff_syntax(syntax)
        assert actual == expected

    def test_change_many(self):
        ref = textwrap.dedent(
            """\
                    line1
                    oldline
                    alsooldline
                    line2
                """
        ).splitlines()
        new = textwrap.dedent(
            """\
                    line1
                    newline
                    alsonewline
                    line2
                """
        ).splitlines()
        syntax, = [
            i.strip() for i in difflib.unified_diff(ref, new, n=0) if i.startswith("@@")
        ]
        assert syntax == "@@ -2,2 +2,2 @@"
        expected = ("change", 2, 2)  # "c",start1,start2
        actual = DiffList._translate_diff_syntax(syntax)
        assert actual == expected

    def test_change_and_insert(self):
        ref = textwrap.dedent(
            """\
                            line1
                            oldline
                            line2
                        """
        ).splitlines()
        new = textwrap.dedent(
            """\
                            line1
                            newline
                            instertme
                            line2
                        """
        ).splitlines()
        syntax, = [
            i.strip() for i in difflib.unified_diff(ref, new, n=0) if i.startswith("@@")
        ]
        assert syntax == "@@ -2 +2,2 @@"
        expected = ("change", 2, 2)  # "c",start1,start2
        actual = DiffList._translate_diff_syntax(syntax)
        assert actual == expected

    def test_change_and_delete(self):
        ref = textwrap.dedent(
            """\
                            line1
                            oldline
                            deleteme
                            line2
                        """
        ).splitlines()
        new = textwrap.dedent(
            """\
                            line1
                            newline
                            line2
                        """
        ).splitlines()
        syntax, = [
            i.strip() for i in difflib.unified_diff(ref, new, n=0) if i.startswith("@@")
        ]
        assert syntax == "@@ -2,2 +2 @@"
        expected = ("change", 2, 2)  # "c",start1,start2
        actual = DiffList._translate_diff_syntax(syntax)
        assert actual == expected

    def test_change_and_insert_offset(self):
        ref = textwrap.dedent(
            """\
                            line1
                            oldline
                            line2
                        """
        ).splitlines()
        new = textwrap.dedent(
            """\
                            line0
                            line1
                            newline
                            instertme
                            line2
                        """
        ).splitlines()
        syntax = [
            i.strip() for i in difflib.unified_diff(ref, new, n=0) if i.startswith("@@")
        ][1]
        assert syntax == "@@ -2 +3,2 @@"
        expected = ("change", 2, 3)  # "c",start1,start2
        actual = DiffList._translate_diff_syntax(syntax)
        assert actual == expected

    def test_malformed1(self):
        expected_msg = "malformed unified diff hunk syntax"

        syntax = "@@ 7 @@"
        with pytest.raises(ValueError) as excinfo:
            DiffList._translate_diff_syntax(syntax)
        assert expected_msg in str(excinfo.value)

        syntax = "@@ 7 10 0 @@"
        with pytest.raises(ValueError) as excinfo:
            DiffList._translate_diff_syntax(syntax)
        assert expected_msg in str(excinfo.value)

        syntax = "@@ 2,3 4,5"
        with pytest.raises(ValueError) as excinfo:
            DiffList._translate_diff_syntax(syntax)
        assert expected_msg in str(excinfo.value)


class Test_DiffList_from_files(object):
    def test_from_files(self):
        filetext1 = textwrap.dedent(
            """\
                    suite foo
                      family bar
                        edit FOOBAR 5
                        task baz
                      endfamily
                    endsuite
                  """
        )
        filetext2 = filetext1.replace("baz", "boo")
        expected = [
            d.context_to_string(no_labels=True)
            for d in DiffList(filetext1, filetext2)._diffs
        ]

        with tempfile.NamedTemporaryFile(mode="w+t", delete=False) as file1:
            file1.write(filetext1)
            file1.seek(0)
            with tempfile.NamedTemporaryFile(mode="w+t", delete=False) as file2:
                file2.write(filetext2)
                file2.seek(0)
                actual = [
                    d.context_to_string(no_labels=True)
                    for d in DiffList.from_files(file1.name, file2.name)._diffs
                ]

        assert expected == actual

    def test_from_files_error(self):
        """
        Test that the correct exception is raised when attempting to
        load from a file that cannot be found.

        """
        # Create an empty temporary directory:
        tmpdir = tempfile.mkdtemp()

        # Construct a path to a file that does not exist:
        invalid_file_path = os.path.join(tmpdir, "file1.def")

        # Verify that the correct exception is raised when the file is not
        # found, making sure to clean up the temporary directory before the
        # test exits regardless of the outcome.
        try:
            with pytest.raises(IOError) as excinfo:
                DiffList.from_files(invalid_file_path, invalid_file_path)
            expected_msg = "failed to load from file"
            assert expected_msg in str(excinfo.value)
        finally:
            os.rmdir(tmpdir)


class Test_DiffList__parse(object):
    def test_parse(self):
        ref = textwrap.dedent(
            """\
                            line1
                            oldline
                            line2
                            deleteme
                            line3
                            line4
                        """
        )
        new = textwrap.dedent(
            """\
                            line1
                            newline
                            line2
                            line3
                            insertme
                            line4
                        """
        )
        input_lines = list(
            difflib.unified_diff(ref.splitlines(True), new.splitlines(True), n=0)
        )
        # ['--- \n',
        #  '+++ \n',
        #  '@@ -2 +2 @@\n',
        #  '-oldline',
        #  '+newline',
        #  '@@ -4 +3,0 @@\n',
        #  '-deleteme',
        #  '@@ -5,0 +5 @@\n',
        #  '+insertme']

        difflist = DiffList(ref, new)
        with patch("cleverdiff.difflist.DiffHunk") as diffhunk_patch, patch(
            "cleverdiff.difflist.DiffHunk._translate_diff_syntax",
            return_value=[("change", 2, 2), ("delete", 4, 3), ("insert", 5, 5)],
        ) as trans_patch:
            difflist._parse(input_lines)

            expected_calls = [
                call(
                    mode="change",
                    content="-oldline\n+newline\n",
                    context=Pair(first=":2", second=":2"),
                    lines=Pair(2, 2),
                ),
                call(
                    mode="delete",
                    content="-deleteme\n",
                    context=Pair(first=":4", second=":3"),
                    lines=Pair(4, 3),
                ),
                call(
                    mode="insert",
                    content="+insertme\n",
                    context=Pair(first=":5", second=":5"),
                    lines=Pair(5, 5),
                ),
            ]
            assert expected_calls == diffhunk_patch.mock_calls
