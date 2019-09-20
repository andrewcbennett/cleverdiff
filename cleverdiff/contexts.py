"""
Defines classes for providing the context of different file types.
See DefaultContext for the interface.

The types in this module should be passed into the `difflist.DiffList` constructor
to specify how to translate line numbers into human-readable strings.
"""


class DefaultContext:
    """A generic context which just returns line numbers."""
    DESCRIPTION = "unformatted text file"

    def __init__(self, filename):
        self.filename = filename

    def __getitem__(self, line):
        """Returns the filename and given line number as a string."""
        return f"{self.filename}:{line}"


class EcflowContext:
    """
    A context class that understands ecFlow suite definitions. These are
    documented at
    https://confluence.ecmwf.int/display/ECFLOW/Definition+file+Grammar.
    """
    DESCRIPTION = "ecFlow suite definition"

    def __init__(self, filename):
        self.filename = filename
        with open(filename, "rt") as f:
            self._context = self._create_context(f.read().splitlines())

    @classmethod
    def _create_context(cls, content):
        """
        Given string content, establish a human-readable context for each
        line. This will be the path of the current node at each line.

        Arguments
        ---------
        content : list of str
            The contents to parse, as a list of strings (one string per line).

        Returns
        -------
        list
            A list of strings describing each line of the content.

        """

        result = []
        stack = [""]
        last_kw = None
        for line in content:
            line = line.strip()
            try:
                keyword, value = line.split()
            except ValueError:
                keyword = line
                value = ''
            if keyword in ['endsuite', 'endfamily']:
                stack.pop()
            if keyword in ['suite', 'family', 'task']:
                if last_kw == 'task':
                    stack.pop()
                last_kw = keyword
                stack.append(value)

            result.append('/'.join(stack))

        return result

    def __getitem__(self, item):
        return f"{self.filename}:{self._context[item]}"


# A dict mapping filename extensions to context classes
EXTENSION_MAPPING = {
    ".def": EcflowContext,
}


def lookup_extension(extension):
    """
    Returns a class type for a given filename extension. If the
    requested extension does not have an associated class type,
    returns `DefaultContext`.

    Arguments
    ---------

    extension : str
        The extension of the filename, including the leading dot.

    Returns
    -------
    type
        A class name representing the context.

    """
    return EXTENSION_MAPPING.get(extension, DefaultContext)
