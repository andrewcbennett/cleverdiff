"""Tests for cleverdiff.py
"""
# pylint: disable=missing-function-docstring, missing-class-docstring
from unittest import mock

import pytest

from cleverdiff.cleverdiff import main


class TestArguments:
    @pytest.mark.parametrize("test_input", ["", "--new", "--old", "--new --old"])
    def test_empty(self, test_input):
        with mock.patch("sys.argv", [""] + test_input.split()):
            with pytest.raises(ValueError) as excinfo:
                main()
        assert "No files specified" in str(excinfo.value)

    @pytest.mark.parametrize("test_input", ["--new file", "--old file"])
    def test_forget_one(self, test_input):
        with mock.patch("sys.argv", [""] + test_input.split()):
            with pytest.raises(ValueError) as excinfo:
                main()
        assert "Both --old and --new" in str(excinfo.value)

    @pytest.mark.parametrize(
        "test_input", ["--old file --new file file2", "--old file file2 --new file"]
    )
    def test_imbalance(self, test_input):
        with mock.patch("sys.argv", [""] + test_input.split()):
            with pytest.raises(ValueError) as excinfo:
                main()
        assert "must be equal" in str(excinfo.value)

    @pytest.mark.parametrize(
        "test_input",
        ["file", "file=", "=file", "file1=file2=", "=file1=file2", "file1=file2=file3"],
    )
    def test_bad_pairs(self, test_input):
        with mock.patch("sys.argv", [""] + test_input.split()):
            with pytest.raises(SystemExit) as excinfo:
                main()
        assert excinfo.value.code == 2

    @pytest.mark.parametrize(
        "test_input",
        [
            "cleverdiff/test_data/ref.def=cleverdiff/test_data/new.def",
            "--old cleverdiff/test_data/ref.def --new cleverdiff/test_data/new.def",
            "cleverdiff/test_data/ref.def=cleverdiff/test_data/new.def "
            "cleverdiff/test_data/ref2.def=cleverdiff/test_data/new2.def",
            "--old cleverdiff/test_data/ref.def cleverdiff/test_data/ref2.def "
            "--new cleverdiff/test_data/new.def cleverdiff/test_data/new2.def",
        ],
    )
    def test_ok(self, test_input, capsys):
        with mock.patch("sys.argv", [""] + test_input.split()):
            main()
            captured = capsys.readouterr()
        assert "detected" in captured.out
        assert "difference" in captured.out
