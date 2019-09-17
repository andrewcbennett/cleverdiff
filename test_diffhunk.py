from __future__ import (absolute_import, division, print_function)  # noqa

import textwrap

from diffhunk import DiffHunk, Pair

class Test_diffhunk(object):
    def test_str_insert(self):
        mode = "insert"
        content = "+  I'm added"
        lines = Pair(34, 34)
        expected = textwrap.dedent("""\
            insert in line 34 vs line 34:
            +  I'm added
        """)
        actual = str(DiffHunk(mode, content, lines))
        assert expected == actual

    def test_str_delete(self):
        mode = "delete"
        content = "-    deleteme\n- and me!"
        lines = Pair(56, 55)
        expected = textwrap.dedent("""\
            delete in line 56 vs line 55:
            -    deleteme
            - and me!
        """)
        actual = str(DiffHunk(mode, content, lines))
        assert expected == actual

    def test_str_change(self):
        mode = "change"
        content = "- line removed\n+ line inserted"
        lines = Pair(1, 2)
        expected = textwrap.dedent("""\
            change in line 1 vs line 2:
            - line removed
            + line inserted
        """)
        actual = str(DiffHunk(mode, content, lines))
        assert expected == actual


class Test_DiffHunk_compare(object):
    def test_compare_same1(self):
        mode = "insert"
        content = "+  I'm added"
        lines = Pair(34, 34)
        dh1 = DiffHunk(mode, content, lines)
        dh2 = DiffHunk(mode, content, lines)
        expected = 0
        actual = dh1.compare(dh2)
        assert expected == actual

    def test_compare_same2(self):
        mode = "delete"
        content = "-    deleteme\n- and me!"
        lines = Pair(56, 55)
        dh1 = DiffHunk(mode, content, lines)
        dh2 = DiffHunk(mode, content, lines)
        expected = 0
        actual = dh1.compare(dh2)
        assert expected == actual

    def test_compare_same3(self):
        mode = "change"
        content = "- line removed\n+ line inserted"
        lines = Pair(1, 2)
        dh1 = DiffHunk(mode, content, lines)
        dh2 = DiffHunk(mode, content, lines)
        expected = 0
        actual = dh1.compare(dh2)
        assert expected == actual

    def test_compare_lines(self):
        mode = "change"
        content = "+ line inserted"
        lines1 = Pair(1, 2)
        lines2 = Pair(3, 4)
        dh1 = DiffHunk(mode, content, lines1)
        dh2 = DiffHunk(mode, content, lines2)
        expected = 1
        actual = dh1.compare(dh2)
        assert expected == actual

    def test_compare_mode(self):
        mode1 = "change"
        mode2 = "insert"
        content = "+ line inserted"
        lines = Pair(1, 2)
        dh1 = DiffHunk(mode1, content, lines)
        dh2 = DiffHunk(mode2, content, lines)
        expected = 2
        actual = dh1.compare(dh2)
        assert expected == actual

    def test_compare_content(self):
        mode = "change"
        content1 = "+ line inserted\n- line removed"
        content2 = "+ different line inserted\n- line removed"
        lines = Pair(1, 2)
        dh1 = DiffHunk(mode, content1, lines)
        dh2 = DiffHunk(mode, content2, lines)
        expected = 2
        actual = dh1.compare(dh2)
        assert expected == actual

    def test_compare_lines_and_content(self):
        mode = "change"
        content1 = "+ line inserted\n- line removed"
        content2 = "+ different line inserted\n- line removed"
        lines1 = Pair(1, 2)
        lines2 = Pair(10, 11)
        dh1 = DiffHunk(mode, content1, lines1)
        dh2 = DiffHunk(mode, content2, lines2)
        expected = 2
        actual = dh1.compare(dh2)
        assert expected == actual

    def test_compare_context_and_content(self):
        mode = "change"
        content1 = "+ line inserted\n- line removed"
        content2 = "+ different line inserted\n- line removed"
        lines = Pair(1, 2)
        dh1 = DiffHunk(mode, content1, lines)
        dh2 = DiffHunk(mode, content2, lines)
        expected = 2
        actual = dh1.compare(dh2)
        assert expected == actual
