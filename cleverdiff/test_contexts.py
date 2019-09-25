import tempfile
import textwrap
from mock import patch

from cleverdiff.contexts import DefaultContext, EcflowContext


class Test_DefaultContext:
    def test_description(self):
        """Ensure there is an appropriate DESCRIPTION attribute."""
        assert hasattr(DefaultContext, "DESCRIPTION")

        expected = "unformatted text file"
        actual = DefaultContext.DESCRIPTION
        assert expected == actual

    def test_getindex(self):
        """Ensure that dict notation returns a sensible string."""
        filename = '/path/to/foobar'
        instance = DefaultContext(filename)

        actual = instance[3]
        expected = f"{filename}:3"
        assert expected == actual

        actual = instance[256]
        expected = f"{filename}:256"
        assert expected == actual


class Test_EcflowContext:
    def test_description(self):
        """Ensure there is an appropriate DESCRIPTION attribute."""
        assert hasattr(EcflowContext, "DESCRIPTION")

        expected = "ecFlow suite definition"
        actual = EcflowContext.DESCRIPTION
        assert expected == actual

    def test_getindex(self):
        """Ensure that dict notation returns a sensible string."""
        filename = '/path/to/foobar'

        with patch("cleverdiff.contexts.EcflowContext._create_context",
                   return_value=["/first", "/second", "/third"]):
            with tempfile.NamedTemporaryFile(mode="wt", delete=False) as f:
                filename = f.name
                instance = EcflowContext(filename)

                actual = instance[0]
                expected = f"{filename}:/first"
                assert expected == actual

                actual = instance[2]
                expected = f"{filename}:/third"
                assert expected == actual

    def test_create_context(self):
        """Ensure that _create_context classmethod behaves as expected."""
        content = textwrap.dedent("""
            suite foo
              limit BAZLIM 10
              family bar
                task bud
                  trigger bar == complete
                  edit SNOOZE 5
                task baz
                  inlimit BAZLIM
                family goo
                  task gunk
                endfamily
              endfamily
              task end
                trigger bar == complete
            endsuite
        """).splitlines(True)
        expected = [
            "",
            "/foo",
            "/foo",
            "/foo/bar",
            "/foo/bar/bud",
            "/foo/bar/bud",
            "/foo/bar/bud",
            "/foo/bar/baz",
            "/foo/bar/baz",
            "/foo/bar/goo",
            "/foo/bar/goo/gunk",
            "/foo/bar/goo",
            "/foo/bar",
            "/foo/end",
            "/foo/end",
            "/foo",
        ]
        actual = EcflowContext._create_context(content)
        assert expected == actual
