from __future__ import absolute_import, division, print_function  # noqa

import textwrap

from cleverdiff.diffhunk import DiffHunk, Pair


class Test_diffhunk(object):

    def test_str_insert(self):
        context = Pair("file1:34", "file2:34")
        mode = "insert"
        content = "+  I'm added"
        lines = Pair(34, 34)
        expected = textwrap.dedent(
            """\
            insert in file1:34 vs file2:34:
            +  I'm added
        """
        )
        actual = str(DiffHunk(mode, content, context, lines))
        assert expected == actual

    def test_str_delete(self):
        context = Pair("file1:56", "file2:55")
        mode = "delete"
        content = "-    deleteme\n- and me!"
        lines = Pair(56, 55)
        expected = textwrap.dedent(
            """\
            delete in file1:56 vs file2:55:
            -    deleteme
            - and me!
        """
        )
        actual = str(DiffHunk(mode, content, context, lines))
        assert expected == actual

    def test_str_change(self):
        context = Pair("file1:1", "file2:2")
        mode = "change"
        content = "- line removed\n+ line inserted"
        lines = Pair(1, 2)
        expected = textwrap.dedent(
            """\
            change in file1:1 vs file2:2:
            - line removed
            + line inserted
        """
        )
        actual = str(DiffHunk(mode, content, context, lines))
        assert expected == actual


class Test_DiffHunk_compare(object):
    CONTEXT = Pair("file1", "file2")

    def test_compare_same1(self):
        mode = "insert"
        content = "+  I'm added"
        lines = Pair(34, 34)
        dh1 = DiffHunk(mode, content, self.CONTEXT, lines)
        dh2 = DiffHunk(mode, content, self.CONTEXT, lines)
        expected = 0
        actual = dh1.compare(dh2)
        assert expected == actual

    def test_compare_same2(self):
        mode = "delete"
        content = "-    deleteme\n- and me!"
        lines = Pair(56, 55)
        dh1 = DiffHunk(mode, content, self.CONTEXT, lines)
        dh2 = DiffHunk(mode, content, self.CONTEXT, lines)
        expected = 0
        actual = dh1.compare(dh2)
        assert expected == actual

    def test_compare_same3(self):
        mode = "change"
        content = "- line removed\n+ line inserted"
        lines = Pair(1, 2)
        dh1 = DiffHunk(mode, content, self.CONTEXT, lines)
        dh2 = DiffHunk(mode, content, self.CONTEXT, lines)
        expected = 0
        actual = dh1.compare(dh2)
        assert expected == actual

    def test_compare_lines(self):
        mode = "change"
        content = "+ line inserted"
        lines1 = Pair(1, 2)
        lines2 = Pair(3, 4)
        dh1 = DiffHunk(mode, content, self.CONTEXT, lines1)
        dh2 = DiffHunk(mode, content, self.CONTEXT, lines2)
        expected = 1
        actual = dh1.compare(dh2)
        assert expected == actual

    def test_compare_mode(self):
        mode1 = "change"
        mode2 = "insert"
        content = "+ line inserted"
        lines = Pair(1, 2)
        dh1 = DiffHunk(mode1, content, self.CONTEXT, lines)
        dh2 = DiffHunk(mode2, content, self.CONTEXT, lines)
        expected = 2
        actual = dh1.compare(dh2)
        assert expected == actual

    def test_compare_content(self):
        mode = "change"
        content1 = "+ line inserted\n- line removed"
        content2 = "+ different line inserted\n- line removed"
        lines = Pair(1, 2)
        dh1 = DiffHunk(mode, content1, self.CONTEXT, lines)
        dh2 = DiffHunk(mode, content2, self.CONTEXT, lines)
        expected = 2
        actual = dh1.compare(dh2)
        assert expected == actual

    def test_compare_lines_and_content(self):
        mode = "change"
        content1 = "+ line inserted\n- line removed"
        content2 = "+ different line inserted\n- line removed"
        lines1 = Pair(1, 2)
        lines2 = Pair(10, 11)
        dh1 = DiffHunk(mode, content1, self.CONTEXT, lines1)
        dh2 = DiffHunk(mode, content2, self.CONTEXT, lines2)
        expected = 2
        actual = dh1.compare(dh2)
        assert expected == actual

    def test_compare_context_and_content(self):
        mode = "change"
        content1 = "+ line inserted\n- line removed"
        content2 = "+ different line inserted\n- line removed"
        lines = Pair(1, 2)
        dh1 = DiffHunk(mode, content1, self.CONTEXT, lines)
        dh2 = DiffHunk(mode, content2, self.CONTEXT, lines)
        expected = 2
        actual = dh1.compare(dh2)
        assert expected == actual
